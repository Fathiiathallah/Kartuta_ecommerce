import json
import base64
import hashlib
import urllib.request
import urllib.error
from django.conf import settings


def get_midtrans_headers():
    server_key = settings.MIDTRANS_SERVER_KEY
    auth_str = base64.b64encode(f"{server_key}:".encode()).decode()
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_str}",
    }


def create_snap_transaction(order):
    """
    Membuat transaksi Snap token di Midtrans untuk sebuah pesanan (HistoryPayment).
    Mengembalikan (snap_token, redirect_url) atau (None, None).
    """
    items = []
    if order.pk and order.items.exists():
        for item in order.items.select_related('product').all():
            items.append({
                "id": str(item.product.id),
                "price": int(item.price),
                "quantity": item.quantity,
                "name": item.product.name[:50],
            })
    elif order.product:
        items.append({
            "id": str(order.product.id),
            "price": int(order.amount),
            "quantity": 1,
            "name": order.product.name[:50],
        })

    # Tambahkan ongkos kirim ke item details jika ada selisih
    items_total = sum(i['price'] * i['quantity'] for i in items)
    gross_amount = int(order.amount)
    diff = gross_amount - items_total
    if diff > 0:
        items.append({
            "id": "SHIPPING-FEE",
            "price": diff,
            "quantity": 1,
            "name": f"Ongkir ({order.courier_service})"[:50],
        })

    payload = {
        "transaction_details": {
            "order_id": order.invoice_number,
            "gross_amount": gross_amount,
        },
        "item_details": items,
        "customer_details": {
            "first_name": (order.shipping_name or order.user_client.username)[:50],
            "email": order.user_client.email or f"{order.user_client.username}@kartuta.id",
            "phone": order.shipping_phone or order.user_client.telp or "081234567890",
            "billing_address": {
                "first_name": (order.shipping_name or order.user_client.username)[:50],
                "phone": order.shipping_phone or order.user_client.telp or "081234567890",
                "address": (order.shipping_address or "Alamat KartuTa")[:200],
                "city": (order.shipping_city or "Makassar")[:50],
            },
            "shipping_address": {
                "first_name": (order.shipping_name or order.user_client.username)[:50],
                "phone": order.shipping_phone or order.user_client.telp or "081234567890",
                "address": (order.shipping_address or "Alamat KartuTa")[:200],
                "city": (order.shipping_city or "Makassar")[:50],
            }
        }
    }

    req = urllib.request.Request(
        settings.MIDTRANS_SNAP_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers=get_midtrans_headers()
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get('token'), data.get('redirect_url')
    except Exception as e:
        print(f"[Midtrans] Error creating Snap transaction: {e}")
        return None, None


def verify_midtrans_signature(order_id, status_code, gross_amount, signature_key):
    """
    Verifikasi keaslian webhook notifikasi Midtrans:
    SHA512(order_id + status_code + gross_amount + ServerKey)
    """
    server_key = settings.MIDTRANS_SERVER_KEY
    raw = f"{order_id}{status_code}{gross_amount}{server_key}"
    calculated = hashlib.sha512(raw.encode('utf-8')).hexdigest()
    return calculated == signature_key
