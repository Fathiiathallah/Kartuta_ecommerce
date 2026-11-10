from django.test import TestCase, Client
from django.contrib.auth.models import User
from app.models import Product, Category, CartItem, HistoryPayment, VirtualBinder, UserClient


class EcommerceFlowTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Era')
        self.product = Product.objects.create(
            name='Test Card',
            category=self.category,
            price=150000,
            stock=5,
            card_grade='Grade A Mint'
        )
        self.user = User.objects.create_user(username='buyer', password='password123')
        self.client_profile = UserClient.objects.create(
            user=self.user,
            username='buyer',
            email='buyer@kartuta.id',
            telp='081234567890',
            alamat='Jl. Contoh No. 1'
        )
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            is_staff=True,
            last_name='Super Admin'
        )

    def test_cart_checkout_and_tracking(self):
        c = Client()
        c.login(username='buyer', password='password123')

        # 1. Add to cart
        c.post(f'/app/keranjang/tambah/{self.product.id}/', {'quantity': 2})
        cart_item = CartItem.objects.filter(user=self.user, product=self.product).first()
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 2)

        # 2. Checkout
        resp = c.post('/app/checkout/', {
            'shipping_name': 'Buyer Name',
            'shipping_phone': '081234567890',
            'shipping_city': 'Makassar',
            'shipping_address': 'Jl. Bunga 123',
            'courier_service': 'J&T Express Reguler',
            'payment_method': 'QRIS Midtrans'
        })
        self.assertEqual(resp.status_code, 302)

        order = HistoryPayment.objects.filter(user_client=self.client_profile).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'Pending')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # 3. User tracking view
        resp = c.get(f'/app/pesanan/{order.invoice_number}/')
        self.assertEqual(resp.status_code, 200)

        # 4. Admin update resi & status
        c_admin = Client()
        c_admin.login(username='admin_test', password='password123')
        resp = c_admin.post(f'/app/admin-pesanan/{order.invoice_number}/', {
            'status': 'Shipped',
            'courier_service': 'J&T Express Reguler',
            'tracking_number_awb': 'JT12345678',
            'tracking_note': 'Paket telah dikirim.'
        })
        self.assertEqual(resp.status_code, 302)

        order.refresh_from_db()
        self.assertEqual(order.status, 'Shipped')
        self.assertEqual(order.tracking_number_awb, 'JT12345678')
        self.assertTrue(VirtualBinder.objects.filter(user_client=self.client_profile, product=self.product).exists())
