from django.core.management.base import BaseCommand

from app.order_expiry import expire_unpaid_orders


class Command(BaseCommand):
    help = 'Batalkan pesanan Pending yang belum dibayar melewati UNPAID_TIMEOUT_MINUTES.'

    def handle(self, *args, **options):
        total = expire_unpaid_orders()
        self.stdout.write(self.style.SUCCESS(f'{total} pesanan dibatalkan otomatis.'))
