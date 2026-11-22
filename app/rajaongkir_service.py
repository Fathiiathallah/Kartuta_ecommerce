"""
Integrasi RajaOngkir (Komerce) — tarif kurir + tracking AWB.

JNE dan J&T tidak membuka API publik untuk developer umum (butuh MOU merchant
korporat), jadi keduanya diakses lewat agregator RajaOngkir yang sudah
terhubung ke sistem JNE/J&T/SiCepat.

Kalau RAJAONGKIR_KEY / RAJAONGKIR_ORIGIN_ID kosong di settings, semua fungsi di
sini mengembalikan kosong dan checkout memakai tarif statis COURIER_RATES.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

BASE = "https://rajaongkir.komerce.id/api/v1"
COURIERS = ("jne", "jnt", "sicepat")
LABEL = {"jne": "JNE", "jnt": "J&T Express", "sicepat": "SiCepat"}
TIMEOUT = 15


def _bersihkan_etd(etd):
    """RajaOngkir kirim '1 day' / '1-2 days' / '1 Hari' — sisakan angkanya saja."""
    teks = re.sub(r'(?i)\b(days?|hari)\b', '', str(etd or '')).strip()
    return teks.rstrip(' -')


def is_enabled():
    return bool(settings.RAJAONGKIR_KEY and settings.RAJAONGKIR_ORIGIN_ID)


def _request(path, data=None):
    headers = {"key": settings.RAJAONGKIR_KEY, "Accept": "application/json", "User-Agent": "Kartuta/1.0"}
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(
        f"{BASE}/{path}", data=body, headers=headers,
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read() or b"{}")


def search_destination(keyword):
    """Cari ID kecamatan tujuan. Return {'results': [{'id','label'}], 'error': str|None}."""
    if not settings.RAJAONGKIR_KEY:
        return {"results": [], "error": "RAJAONGKIR_KEY belum diisi di .env aplikasi"}
    if not keyword:
        return {"results": [], "error": None}
    query = urllib.parse.urlencode({"search": keyword, "limit": 15, "offset": 0})
    try:
        data = _request(f"destination/domestic-destination?{query}")
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = json.loads(e.read() or b"{}").get("meta", {}).get("message", "")
        except ValueError:
            pass
        return {"results": [], "error": f"RajaOngkir HTTP {e.code} {detail}".strip()}
    except (urllib.error.URLError, ValueError) as e:
        return {"results": [], "error": f"Gagal hubungi RajaOngkir: {e}"}
    results = [
        {
            "id": str(d.get("id", "")),
            "label": d.get("label") or d.get("subdistrict_name") or "",
        }
        for d in (data.get("data") or [])
        if d.get("id")
    ]
    return {"results": results, "error": None}


def shipping_options(destination_id, weight_gram):
    """Opsi ongkir JNE/J&T/SiCepat. Return [] kalau API mati / data kurang."""
    if not is_enabled() or not destination_id or not weight_gram:
        return []
    weight_gram = max(int(weight_gram), 1000)  # tarif kurir minimum 1 kg
    cache_key = f"ongkir:{settings.RAJAONGKIR_ORIGIN_ID}:{destination_id}:{weight_gram}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    options = []
    for courier in COURIERS:
        payload = {
            "origin": settings.RAJAONGKIR_ORIGIN_ID,
            "destination": destination_id,
            "weight": weight_gram,
            "courier": courier,
            "price": "lowest",
        }
        try:
            data = _request("calculate/domestic-cost", payload)
        except (urllib.error.URLError, ValueError):
            continue  # kurir tidak melayani rute ini
        for d in data.get("data") or []:
            cost = int(d.get("cost") or 0)
            service_name = (d.get("service") or "").upper()
            # Lewati layanan kargo/truk (JNE JTR, SiCepat GOKIL) yang minimum ~10 kg
            if "GOKIL" in service_name or service_name.startswith("JTR"):
                continue
            if weight_gram <= 5000 and cost > 50000:
                continue
            options.append({
                "label": f"{LABEL.get(d.get('code'), d.get('code', '').upper())} {(d.get('service') or '').replace('CTCEYES', 'CTC YES').replace('CTCYES', 'CTC YES')}".strip(),
                "courier": d.get("code", ""),
                "service": d.get("service", ""),
                "cost": cost,
                "etd": _bersihkan_etd(d.get("etd")),
            })
    if options:
        cache.set(cache_key, options, 600)
    return options


def track(awb, courier, last_phone_number=""):
    """Ambil riwayat AWB. last_phone_number = 5 digit terakhir HP penerima (wajib JNE)."""
    if not settings.RAJAONGKIR_KEY or not awb or not courier:
        return {}
    query = {"awb": awb, "courier": courier}
    if last_phone_number:
        query["last_phone_number"] = last_phone_number
    try:
        data = _request(f"track/waybill?{urllib.parse.urlencode(query)}")
    except (urllib.error.URLError, ValueError):
        return {}
    return data.get("data") or {}


def track_history(data):
    """
    Normalisasi riwayat tracking jadi [{'status','note'}].
    ponytail: bentuk history beda per kurir, jadi ambil kunci yang ada saja.
    Kalau format baru muncul, tambah kuncinya di sini.
    """
    if not data:
        return []
    details = data.get("details") or {}
    history = data.get("history") or (details.get("history") if isinstance(details, dict) else None) or []
    entries = []
    for item in history:
        note = (item.get("desc") or item.get("description") or item.get("note")
                or item.get("manifest_description") or item.get("status") or "")
        status = item.get("status") or item.get("manifest_code") or "Transit"
        date = item.get("date") or item.get("manifest_date") or item.get("datetime") or ""
        entries.append({
            "status": str(status)[:50],
            "note": f"{date} — {note}".strip(" —")[:255] if date else str(note)[:255],
        })
    if not entries and isinstance(details, dict) and details.get("status"):
        entries.append({"status": str(details["status"])[:50], "note": str(data.get("summary", {}).get("status", ""))[:255]})
    return entries
