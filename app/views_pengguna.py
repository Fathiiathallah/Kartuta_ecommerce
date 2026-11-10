import datetime
import uuid
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .form_pengguna import formProfile
from .models import (
    UserPengguna, UserClient, VirtualBinder, HistoryPayment,
    Product, Category, CartItem, OrderItem, OrderTrackingLog
)
from .decorators_admin import pengguna_required
from .midtrans_service import create_snap_transaction, verify_midtrans_signature


def get_or_create_user_client(user):
    user_client = UserClient.objects.filter(user=user).first()
    if not user_client:
        user_client = UserClient.objects.filter(username=user.username).first()
        if user_client and not user_client.user:
            user_client.user = user
            user_client.save()
        elif not user_client:
            user_client = UserClient.objects.create(
                user=user,
                username=user.username,
                email=user.email or f"{user.username}@kartuta.id",
                alamat="",
                telp="",
            )
    return user_client

@login_required
@pengguna_required
def profile_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if not userpengguna:
        userpengguna = UserPengguna.objects.filter(username=request.user.username).first()
        if userpengguna and not userpengguna.user:
            userpengguna.user = request.user
            userpengguna.save()
        elif not userpengguna:
            userpengguna = UserPengguna.objects.create(
                user=request.user,
                username=request.user.username,
                email=request.user.email or request.user.username
            )

    if request.method == 'POST':
        form = formProfile(request.POST, request.FILES, instance=userpengguna)
        if form.is_valid():
            pengguna = form.save(commit=False)
            pengguna.user = request.user
            pengguna.save()
            messages.success(request, 'Data profil pengguna berhasil disimpan!')
            return redirect('app:profile_pengguna')
        else:
            messages.error(request, 'Data profil belum lengkap atau terjadi kesalahan pengisian. Silakan periksa kembali.')
    else:
        form = formProfile(instance=userpengguna)

    context = {
        'title': 'Profil Pengguna',
        'heading': 'Profil Kolektor KartuTa',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'form': form,
    }
    return render(request, 'pengguna/profil_pengguna.html', context)


@login_required
@pengguna_required
def dashboard_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if not userpengguna:
        userpengguna = UserPengguna.objects.filter(username=request.user.username).first()

    binders = VirtualBinder.objects.filter(user_client=userpengguna) if userpengguna else []
    payments = HistoryPayment.objects.filter(user_client=userpengguna).order_by('-payment_date') if userpengguna else []

    context = {
        'title': 'Dashboard',
        'heading': 'Dashboard Pengguna',
        'userdetail': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'binders': binders,
        'payments': payments,
    }
    return render(request, 'pengguna/index.html', context)


@login_required
@pengguna_required
def katalog_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if not userpengguna:
        userpengguna = UserPengguna.objects.filter(username=request.user.username).first()

    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id).select_related('category').order_by('-created_at')
    else:
        products = Product.objects.select_related('category').all().order_by('-created_at')

    categories = Category.objects.all()

    context = {
        'title': 'Katalog Photocard',
        'heading': 'Etalase Official Photocard',
        'userdetail': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'products': products,
        'categories': categories,
        'active_category': category_id,
    }
    return render(request, 'pengguna/katalog.html', context)


# ==============================================================================
# KERANJANG (CART)
# ==============================================================================

@login_required
def cart_list(request):
    user_client = get_or_create_user_client(request.user)
    cart_items = CartItem.objects.filter(user=request.user).select_related('product', 'product__category')
    subtotal = sum(item.subtotal() for item in cart_items)
    total_qty = sum(item.quantity for item in cart_items)

    context = {
        'title': 'Keranjang Koleksi',
        'heading': 'Keranjang Belanja Photocard',
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_qty': total_qty,
        'userdetail': user_client,
        'photo': user_client.photo if user_client and user_client.photo else None,
    }
    return render(request, 'pengguna/cart.html', context)


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.stock <= 0:
        messages.error(request, f'Maaf, stok photocard "{product.name}" sudah habis!')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        qty = 1

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        if cart_item.quantity + qty > product.stock:
            cart_item.quantity = product.stock
            messages.warning(request, f'Jumlah disesuaikan dengan sisa stok ({product.stock} pcs).')
        else:
            cart_item.quantity += qty
            messages.success(request, f'"{product.name}" ditambahkan ke keranjang.')
    else:
        cart_item.quantity = min(qty, product.stock)
        messages.success(request, f'"{product.name}" berhasil dimasukkan ke keranjang!')

    cart_item.save()

    # Direct buy option (Beli Sekarang)
    if request.POST.get('buy_now') or request.GET.get('direct'):
        return redirect('app:checkout')

    return redirect(request.META.get('HTTP_REFERER', 'app:cart_list'))


@login_required
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')

    if action == 'plus':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f'Maksimum stok tersedia: {cart_item.product.stock} pcs.')
    elif action == 'minus':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, f'"{cart_item.product.name}" dihapus dari keranjang.')
    elif 'quantity' in request.POST:
        try:
            qty = int(request.POST['quantity'])
            if qty <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = min(qty, cart_item.product.stock)
                cart_item.save()
        except ValueError:
            pass

    return redirect('app:cart_list')


@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Produk telah dihapus dari keranjang.')
    return redirect('app:cart_list')


# ==============================================================================
# CHECKOUT
# ==============================================================================

COURIER_RATES = {
    'J&T Express Reguler': 18000,
    'JNE Reguler': 20000,
    'SiCepat BEST': 25000,
}

@login_required
def checkout(request):
    user_client = get_or_create_user_client(request.user)
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')

    if not cart_items.exists():
        messages.warning(request, 'Keranjang belanja Anda kosong. Silakan pilih photocard terlebih dahulu.')
        return redirect('app:cart_list')

    # Periksa stok
    for item in cart_items:
        if item.product.stock < item.quantity:
            messages.error(request, f'Stok "{item.product.name}" tidak mencukupi (sisa: {item.product.stock}).')
            return redirect('app:cart_list')

    subtotal = sum(item.subtotal() for item in cart_items)
    total_qty = sum(item.quantity for item in cart_items)

    if request.method == 'POST':
        shipping_name = request.POST.get('shipping_name', '').strip() or request.user.get_full_name() or request.user.username
        shipping_phone = request.POST.get('shipping_phone', '').strip() or user_client.telp or ''
        shipping_address = request.POST.get('shipping_address', '').strip() or user_client.alamat or ''
        shipping_city = request.POST.get('shipping_city', '').strip()
        courier_service = request.POST.get('courier_service', 'J&T Express Reguler')
        payment_method = request.POST.get('payment_method', 'QRIS Midtrans')
        notes = request.POST.get('notes', '').strip()

        if not shipping_address or not shipping_phone:
            messages.error(request, 'Mohon lengkapi nomor telepon dan alamat pengiriman!')
            return redirect('app:checkout')

        shipping_cost = COURIER_RATES.get(courier_service, 18000)
        total_amount = subtotal + shipping_cost

        # Generate Invoice
        now_str = datetime.datetime.now().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:6].upper()
        invoice_number = f"KT-{now_str}-{unique_suffix}"

        first_product = cart_items.first().product

        order = HistoryPayment.objects.create(
            user_client=user_client,
            product=first_product,
            invoice_number=invoice_number,
            amount=total_amount,
            payment_method=payment_method,
            courier_service=courier_service,
            status='Pending',
            shipping_name=shipping_name,
            shipping_phone=shipping_phone,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            notes=notes
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Kurangi stok produk
            item.product.stock = max(0, item.product.stock - item.quantity)
            item.product.save(update_fields=['stock'])

        # Tracking log perdana
        OrderTrackingLog.objects.create(
            order=order,
            status='Pending',
            note='Pesanan berhasil dibuat. Menunggu konfirmasi pembayaran.'
        )

        # Kosongkan keranjang
        cart_items.delete()

        messages.success(request, f'Pesanan #{order.invoice_number} berhasil dibuat!')
        return redirect('app:pesanan_detail', invoice_number=order.invoice_number)

    default_courier = 'J&T Express Reguler'
    default_shipping_cost = COURIER_RATES.get(default_courier, 18000)

    context = {
        'title': 'Checkout Pengiriman',
        'heading': 'Checkout & Konfirmasi Pengiriman',
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_qty': total_qty,
        'courier_rates': COURIER_RATES,
        'default_shipping_cost': default_shipping_cost,
        'grand_total': subtotal + default_shipping_cost,
        'userdetail': user_client,
        'photo': user_client.photo if user_client and user_client.photo else None,
    }
    return render(request, 'pengguna/checkout.html', context)


# ==============================================================================
# TRACKING PEMESANAN PENGGUNA
# ==============================================================================

@login_required
def pesanan_saya(request):
    user_client = get_or_create_user_client(request.user)
    status_filter = request.GET.get('status')

    orders = HistoryPayment.objects.filter(user_client=user_client).prefetch_related('items', 'items__product').order_by('-payment_date')
    if status_filter:
        orders = orders.filter(status=status_filter)

    counts = {
        'all': HistoryPayment.objects.filter(user_client=user_client).count(),
        'pending': HistoryPayment.objects.filter(user_client=user_client, status='Pending').count(),
        'completed': HistoryPayment.objects.filter(user_client=user_client, status='Completed').count(),
        'packing': HistoryPayment.objects.filter(user_client=user_client, status='Packing').count(),
        'shipped': HistoryPayment.objects.filter(user_client=user_client, status='Shipped').count(),
        'delivered': HistoryPayment.objects.filter(user_client=user_client, status='Delivered').count(),
    }

    context = {
        'title': 'Tracking & Pesanan Saya',
        'heading': 'Daftar & Status Pesanan Saya',
        'orders': orders,
        'status_filter': status_filter,
        'counts': counts,
        'userdetail': user_client,
        'photo': user_client.photo if user_client and user_client.photo else None,
    }
    return render(request, 'pengguna/pesanan_list.html', context)


@login_required
def pesanan_detail(request, invoice_number):
    user_client = get_or_create_user_client(request.user)
    # Staf/Admin juga diizinkan melihat jika mengakses link ini
    if request.user.is_staff or request.user.last_name == 'Super Admin':
        order = get_object_or_404(
            HistoryPayment.objects.select_related('user_client').prefetch_related('items', 'items__product', 'tracking_logs'),
            invoice_number=invoice_number
        )
    else:
        order = get_object_or_404(
            HistoryPayment.objects.select_related('user_client').prefetch_related('items', 'items__product', 'tracking_logs'),
            invoice_number=invoice_number,
            user_client=user_client
        )

    snap_token = None
    snap_redirect_url = None
    if order.status == 'Pending':
        snap_token, snap_redirect_url = create_snap_transaction(order)

    context = {
        'title': f'Tracking Pesanan #{order.invoice_number}',
        'heading': f'Detail & Status Pengiriman',
        'order': order,
        'logs': order.tracking_logs.all(),
        'userdetail': user_client,
        'photo': user_client.photo if user_client and user_client.photo else None,
        'snap_token': snap_token,
        'snap_redirect_url': snap_redirect_url,
        'midtrans_client_key': settings.MIDTRANS_CLIENT_KEY,
        'midtrans_snap_js': settings.MIDTRANS_SNAP_JS,
    }
    return render(request, 'pengguna/pesanan_detail.html', context)


@login_required
def pesanan_bayar_simulasi(request, invoice_number):
    user_client = get_or_create_user_client(request.user)
    order = get_object_or_404(HistoryPayment, invoice_number=invoice_number, user_client=user_client)

    if order.status == 'Pending':
        order.status = 'Completed'
        order.save(update_fields=['status', 'updated_at'])
        OrderTrackingLog.objects.create(
            order=order,
            status='Completed',
            note='Pembayaran QRIS Midtrans berhasil diverifikasi secara instan.'
        )
        order.unlock_virtual_binder()
        messages.success(request, 'Pembayaran berhasil dikonfirmasi! Slot Virtual Binder koleksi Anda telah terbuka.')
    else:
        messages.info(request, 'Status pesanan ini sudah bukan menunggu pembayaran.')

    return redirect('app:pesanan_detail', invoice_number=order.invoice_number)


@login_required
def pesanan_konfirmasi_terima(request, invoice_number):
    user_client = get_or_create_user_client(request.user)
    order = get_object_or_404(HistoryPayment, invoice_number=invoice_number, user_client=user_client)

    if order.status == 'Shipped':
        order.status = 'Delivered'
        order.save(update_fields=['status', 'updated_at'])
        OrderTrackingLog.objects.create(
            order=order,
            status='Delivered',
            note='Paket photocard telah diterima dengan baik oleh pelanggan. Transaksi selesai.'
        )
        order.unlock_virtual_binder()
        messages.success(request, 'Terima kasih telah berbelanja di KartuTa! Pesanan Anda telah selesai.')
    else:
        messages.warning(request, 'Pesanan belum dalam status pengiriman kurir.')

    return redirect('app:pesanan_detail', invoice_number=order.invoice_number)


# ==============================================================================
# MIDTRANS HTTP WEBHOOK NOTIFICATION
# ==============================================================================

@csrf_exempt
def midtrans_notification(request):
    """
    Endpoint Webhook Notifikasi HTTP dari Midtrans ketika pembayaran selesai.
    """
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    order_id = data.get('order_id')
    status_code = data.get('status_code')
    gross_amount = data.get('gross_amount')
    signature_key = data.get('signature_key')
    transaction_status = data.get('transaction_status')
    fraud_status = data.get('fraud_status')
    payment_type = data.get('payment_type', 'Midtrans')

    if not verify_midtrans_signature(order_id, status_code, gross_amount, signature_key):
        return JsonResponse({"status": "error", "message": "Invalid signature"}, status=403)

    order = HistoryPayment.objects.filter(invoice_number=order_id).first()
    if not order:
        return JsonResponse({"status": "error", "message": "Order not found"}, status=404)

    if transaction_status in ['capture', 'settlement']:
        if fraud_status is None or fraud_status == 'accept':
            if order.status != 'Completed':
                order.status = 'Completed'
                order.payment_method = f"Midtrans ({payment_type.upper()})"
                order.save(update_fields=['status', 'payment_method', 'updated_at'])
                order.unlock_virtual_binder()
                OrderTrackingLog.objects.create(
                    order=order,
                    status='Completed',
                    note=f'Pembayaran via Midtrans {payment_type.upper()} berhasil diverifikasi otomatis.'
                )
    elif transaction_status in ['cancel', 'deny', 'expire']:
        if order.status == 'Pending':
            order.status = 'Failed'
            order.save(update_fields=['status', 'updated_at'])
            OrderTrackingLog.objects.create(
                order=order,
                status='Failed',
                note=f'Transaksi Midtrans {transaction_status}.'
            )

    return JsonResponse({"status": "ok"})
