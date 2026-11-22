"""Pembatalan otomatis pesanan yang belum dibayar melewati batas waktu."""
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def expire_unpaid_orders():
    """Batalkan pesanan Pending yang lewat UNPAID_TIMEOUT_MINUTES. Return jumlah yang dibatalkan."""
    from .models import HistoryPayment

    batas = timezone.now() - timedelta(minutes=settings.UNPAID_TIMEOUT_MINUTES)
    alasan = (
        'Otomatis dibatalkan: belum dibayar dalam '
        f'{settings.UNPAID_TIMEOUT_MINUTES} menit.'
    )
    total = 0
    for order in HistoryPayment.objects.filter(status='Pending', payment_date__lt=batas):
        if order.cancel(alasan):
            total += 1
    return total
