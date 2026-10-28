from django.db import models
from django.contrib.auth.models import User


class Provinsi(models.Model):
    nama_provinsi = models.CharField(max_length=100)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.nama_provinsi


class UserAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_profile')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, blank=True)
    role_divisi = models.CharField(max_length=50, default='Operations & QC')
    telp = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='admin_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role_divisi}"


class UserClient(models.Model):
    TIER_CHOICES = [
        ('Basic', 'Basic (Gratis)'),
        ('Collector Pro', 'Collector Pro (Rp35.000/bln)'),
        ('Merchant', 'Merchant Tier (Rp150.000/bln)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='client_profile')
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    telp = models.CharField(max_length=20, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    alamat = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='client_photos/', blank=True, null=True)
    provinsi_anggota = models.ForeignKey(Provinsi, on_delete=models.SET_NULL, null=True, blank=True)
    membership_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='Basic')
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.phone_number and not self.telp:
            self.telp = self.phone_number
        elif self.telp and not self.phone_number:
            self.phone_number = self.telp
        if self.shipping_address and not self.alamat:
            self.alamat = self.shipping_address
        elif self.alamat and not self.shipping_address:
            self.shipping_address = self.alamat
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.membership_tier})"


UserPengguna = UserClient


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MediaGambarProduk(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    GRADE_CHOICES = [
        ('Grade A Mint', 'Grade A (Mint Condition 100% Mulus)'),
        ('Grade B Slight', 'Grade B (Slight Factory Scratch)'),
    ]
    name = models.CharField(max_length=200)
    fandom_group = models.CharField(max_length=100, default='aespa')
    member_bias = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    card_grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='Grade A Mint')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image_utama = models.ImageField(upload_to='product_main_images/', blank=True, null=True)
    gambar_tambahan = models.ManyToManyField(MediaGambarProduk, blank=True, related_name='products')
    video_grading_360 = models.FileField(upload_to='product_videos_360/', blank=True, null=True)
    is_official_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.card_grade})"


class HistoryPayment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Menunggu Pembayaran QRIS'),
        ('Completed', 'Lunas Terverifikasi (Midtrans)'),
        ('Packing', 'Sedang Dipacking (4-Layer Gold Safety)'),
        ('Shipped', 'Dalam Pengiriman Kurir (J&T/JNE)'),
        ('Delivered', 'Paket Diterima Customer'),
        ('Failed', 'Batal / Waktu Habis'),
    ]
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='payments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='QRIS Midtrans')
    courier_service = models.CharField(max_length=50, default='J&T Express Reguler')
    tracking_number_awb = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_number} - {self.status}"


class VirtualBinder(models.Model):
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='virtual_binder')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    era_album_template = models.CharField(max_length=100)
    slot_number = models.PositiveIntegerField()
    is_unlocked = models.BooleanField(default=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Binder {self.user_client.username} - Slot #{self.slot_number}"
