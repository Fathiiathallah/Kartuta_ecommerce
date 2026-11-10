from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


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
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='QRIS Midtrans')
    courier_service = models.CharField(max_length=50, default='J&T Express Reguler')
    tracking_number_awb = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    shipping_name = models.CharField(max_length=150, blank=True, null=True)
    shipping_phone = models.CharField(max_length=30, blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def display_products(self):
        items_list = self.items.select_related('product').all()
        if items_list.exists():
            return ", ".join([f"{item.product.name} (x{item.quantity})" for item in items_list])
        if self.product:
            return self.product.name
        return "-"

    @property
    def total_quantity(self):
        items_list = self.items.all()
        if items_list.exists():
            return sum(item.quantity for item in items_list)
        return 1

    @property
    def status_step(self):
        mapping = {
            'Pending': 1,
            'Completed': 2,
            'Packing': 3,
            'Shipped': 4,
            'Delivered': 5,
            'Failed': 0,
        }
        return mapping.get(self.status, 1)

    def unlock_virtual_binder(self):
        if not self.user_client:
            return
        products_to_unlock = []
        if self.items.exists():
            products_to_unlock = [item.product for item in self.items.select_related('product', 'product__category').all()]
        elif self.product:
            products_to_unlock = [self.product]

        for prod in products_to_unlock:
            if not VirtualBinder.objects.filter(user_client=self.user_client, product=prod).exists():
                next_slot = VirtualBinder.objects.filter(user_client=self.user_client).count() + 1
                VirtualBinder.objects.create(
                    user_client=self.user_client,
                    product=prod,
                    era_album_template=prod.category.name if prod.category else 'Official Era',
                    slot_number=next_slot,
                    is_unlocked=True
                )

    def __str__(self):
        return f"{self.invoice_number} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(HistoryPayment, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.order.invoice_number} - {self.product.name} (x{self.quantity})"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"


class OrderTrackingLog(models.Model):
    order = models.ForeignKey(HistoryPayment, on_delete=models.CASCADE, related_name='tracking_logs')
    status = models.CharField(max_length=50)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order.invoice_number} - {self.status}"


class VirtualBinder(models.Model):
    user_client = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='virtual_binder')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    era_album_template = models.CharField(max_length=100)
    slot_number = models.PositiveIntegerField()
    is_unlocked = models.BooleanField(default=True)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Binder {self.user_client.username} - Slot #{self.slot_number}"


# ==============================================================================
# ARTIKEL & HALAMAN
# ==============================================================================

class KategoriArtikel(models.Model):
    nama_kategori = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    deskripsi = models.TextField(blank=True, null=True)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama_kategori)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama_kategori

    class Meta:
        verbose_name = 'Kategori Artikel'
        verbose_name_plural = 'Kategori Artikel'


class Artikel(models.Model):
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    kategori = models.ForeignKey(KategoriArtikel, on_delete=models.CASCADE, related_name='artikel_list')
    penulis = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='artikel_penulis')
    konten = models.TextField()
    gambar_utama = models.ImageField(upload_to='artikel_images/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name='Total Views')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name = 'Artikel'
        verbose_name_plural = 'Artikel'
        ordering = ['-created_at']


class Halaman(models.Model):
    judul = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    konten = models.TextField()
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

    class Meta:
        verbose_name = 'Halaman'
        verbose_name_plural = 'Halaman'


# ==============================================================================
# TAMPILAN & MITRA
# ==============================================================================

class HeroSlide(models.Model):
    judul = models.CharField(max_length=200)
    subjudul = models.TextField(blank=True, null=True)
    gambar = models.ImageField(upload_to='hero_slides/', blank=True, null=True)
    link_url = models.CharField(max_length=255, default='#katalog-etalase')
    tombol_teks = models.CharField(max_length=50, default='Jelajahi Etalase ↓')
    badge_text = models.CharField(max_length=100, default='INDONESIA FIRST HYBRID PHOTOCARD ECOSYSTEM')
    urutan = models.PositiveIntegerField(default=0)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Slide #{self.urutan}: {self.judul}"

    class Meta:
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slide'
        ordering = ['urutan', '-created_at']


class KerjaSama(models.Model):
    nama_mitra = models.CharField(max_length=100)
    kategori_mitra = models.CharField(max_length=50, default='Ekspedisi & Kurir')
    logo = models.ImageField(upload_to='mitra_logos/', blank=True, null=True)
    link_url = models.CharField(max_length=255, blank=True, null=True)
    deskripsi = models.CharField(max_length=200, blank=True, null=True)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_mitra

    class Meta:
        verbose_name = 'Kerja Sama'
        verbose_name_plural = 'Kerja Sama'


class WebSetting(models.Model):
    nama_organisasi = models.CharField(max_length=200, default='KartuTa Indonesia')
    alamat = models.TextField(default='Jl. Kesejahteraan Timur No. 6, makassar, Sulawesi Selatan, Indonesia')
    no_telp = models.CharField(max_length=20, default='+62 812-3456-7890')
    email = models.EmailField(default='contact@kartuta.id')
    logo = models.ImageField(upload_to='web_setting/logo/', blank=True, null=True)
    favicon = models.ImageField(upload_to='web_setting/favicon/', blank=True, null=True)
    link_instagram = models.URLField(blank=True, null=True, default='https://instagram.com/kartuta.official')
    link_maps = models.URLField(blank=True, null=True, default='https://maps.google.com')

    def __str__(self):
        return self.nama_organisasi

    class Meta:
        verbose_name = 'Web Setting'
        verbose_name_plural = 'Web Setting'

