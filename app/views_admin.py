from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import (
    UserAdmin, UserPengguna, Product, Category, HistoryPayment,
    KategoriArtikel, Artikel, Halaman, HeroSlide, KerjaSama,
    OrderItem, CartItem, OrderTrackingLog
)
from .form_admin import (
    formProfile, CategoryForm, ProductForm,
    KategoriArtikelForm, ArtikelForm, HalamanForm, HeroSlideForm, KerjaSamaForm
)
from .decorators_admin import admin_required


def get_admin_data(request):
    useradmin = (
        UserAdmin.objects.filter(user=request.user).first() or
        UserAdmin.objects.filter(username=request.user.username).first() or
        UserAdmin.objects.filter(email=request.user.email).first()
    )
    if useradmin and not useradmin.user:
        useradmin.user = request.user
        useradmin.save()
    elif not useradmin:
        useradmin = UserAdmin.objects.create(
            user=request.user,
            username=request.user.username,
            email=request.user.email or f"{request.user.username}@kartuta.id",
            role_divisi='Operations & QC'
        )
    photo = useradmin.photo if useradmin and useradmin.photo else None
    return useradmin, photo


@admin_required
def profile_admin(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = formProfile(request.POST, request.FILES, instance=useradmin)
        if form.is_valid():
            adm = form.save(commit=False)
            adm.user = request.user
            adm.save()
            messages.success(request, 'Profil Admin berhasil diperbarui!')
            return redirect('app:profile_admin')
        else:
            messages.error(request, 'Gagal memperbarui profil. Periksa isian form.')
    else:
        form = formProfile(instance=useradmin)

    context = {
        'title': 'Profile Admin',
        'heading': 'Edit Profile Admin',
        'useradmin': useradmin,
        'photo': photo,
        'form': form,
    }
    return render(request, 'admin_super/profile_admin.html', context)


@admin_required
def dashboard_admin(request):
    useradmin, photo = get_admin_data(request)

    stats = {
        'total_clients': UserPengguna.objects.count(),
        'total_products': Product.objects.count(),
        'total_categories': Category.objects.count(),
        'total_orders': HistoryPayment.objects.count(),
    }
    clients = UserPengguna.objects.all().order_by('-date_joined')[:10]

    context = {
        'title': 'Dashboard',
        'heading': 'Dashboard Administrator',
        'photo': photo,
        'userdetail': useradmin,
        'stats': stats,
        'clients': clients,
    }
    return render(request, 'admin_super/index.html', context)


# ==============================================================================
# CRUD KATEGORI
# ==============================================================================

@admin_required
def kategori_list(request):
    useradmin, photo = get_admin_data(request)
    categories = Category.objects.all().order_by('-created_at')

    context = {
        'title': 'Kelola Kategori',
        'heading': 'Daftar Kategori Photocard',
        'photo': photo,
        'userdetail': useradmin,
        'categories': categories,
    }
    return render(request, 'admin_super/kategori_list.html', context)


@admin_required
def kategori_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            kategori = form.save()
            messages.success(request, f'Kategori "{kategori.name}" berhasil ditambahkan!')
            return redirect('app:kategori_list')
        else:
            messages.error(request, 'Gagal menambahkan kategori. Periksa input data.')
    else:
        form = CategoryForm()

    context = {
        'title': 'Tambah Kategori',
        'heading': 'Tambah Kategori Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/kategori_form.html', context)


@admin_required
def kategori_edit(request, id):
    useradmin, photo = get_admin_data(request)
    kategori = get_object_or_404(Category, id=id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, f'Kategori "{kategori.name}" berhasil diperbarui!')
            return redirect('app:kategori_list')
        else:
            messages.error(request, 'Gagal memperbarui kategori. Periksa input data.')
    else:
        form = CategoryForm(instance=kategori)

    context = {
        'title': 'Edit Kategori',
        'heading': f'Edit Kategori: {kategori.name}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'kategori': kategori,
        'is_edit': True,
    }
    return render(request, 'admin_super/kategori_form.html', context)


@admin_required
def kategori_hapus(request, id):
    kategori = get_object_or_404(Category, id=id)
    nama = kategori.name
    kategori.delete()
    messages.success(request, f'Kategori "{nama}" berhasil dihapus!')
    return redirect('app:kategori_list')


# ==============================================================================
# CRUD PRODUK
# ==============================================================================

@admin_required
def produk_list(request):
    useradmin, photo = get_admin_data(request)
    products = Product.objects.select_related('category').all().order_by('-created_at')

    context = {
        'title': 'Kelola Produk',
        'heading': 'Daftar Katalog Photocard Official',
        'photo': photo,
        'userdetail': useradmin,
        'products': products,
    }
    return render(request, 'admin_super/produk_list.html', context)


@admin_required
def produk_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save()
            messages.success(request, f'Produk "{prod.name}" berhasil ditambahkan ke etalase!')
            return redirect('app:produk_list')
        else:
            messages.error(request, 'Gagal menambahkan produk. Harap lengkapi field yang diperlukan.')
    else:
        form = ProductForm()

    context = {
        'title': 'Tambah Produk',
        'heading': 'Tambah Photocard Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/produk_form.html', context)


@admin_required
def produk_edit(request, id):
    useradmin, photo = get_admin_data(request)
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Data produk "{product.name}" berhasil disimpan!')
            return redirect('app:produk_list')
        else:
            messages.error(request, 'Gagal memperbarui produk. Periksa input data.')
    else:
        form = ProductForm(instance=product)

    context = {
        'title': 'Edit Produk',
        'heading': f'Edit Photocard: {product.name}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'product': product,
        'is_edit': True,
    }
    return render(request, 'admin_super/produk_form.html', context)


@admin_required
def produk_hapus(request, id):
    product = get_object_or_404(Product, id=id)
    nama = product.name
    product.delete()
    messages.success(request, f'Produk "{nama}" berhasil dihapus dari etalase!')
    return redirect('app:produk_list')


# ==============================================================================
# CRUD KATEGORI ARTIKEL
# ==============================================================================

@admin_required
def kategori_artikel_list(request):
    useradmin, photo = get_admin_data(request)
    kategori_list = KategoriArtikel.objects.all().order_by('-created_at')

    context = {
        'title': 'Kategori Artikel',
        'heading': 'Kelola Kategori Artikel & Panduan',
        'photo': photo,
        'userdetail': useradmin,
        'kategori_list': kategori_list,
    }
    return render(request, 'admin_super/kategori_artikel_list.html', context)


@admin_required
def kategori_artikel_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = KategoriArtikelForm(request.POST)
        if form.is_valid():
            kategori = form.save()
            messages.success(request, f'Kategori artikel "{kategori.nama_kategori}" berhasil ditambahkan!')
            return redirect('app:kategori_artikel_list')
        else:
            messages.error(request, 'Gagal menambahkan kategori. Periksa input data.')
    else:
        form = KategoriArtikelForm()

    context = {
        'title': 'Tambah Kategori Artikel',
        'heading': 'Tambah Kategori Artikel Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/kategori_artikel_form.html', context)


@admin_required
def kategori_artikel_edit(request, id):
    useradmin, photo = get_admin_data(request)
    kategori = get_object_or_404(KategoriArtikel, id=id)

    if request.method == 'POST':
        form = KategoriArtikelForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, f'Kategori artikel "{kategori.nama_kategori}" berhasil diperbarui!')
            return redirect('app:kategori_artikel_list')
        else:
            messages.error(request, 'Gagal memperbarui kategori. Periksa input data.')
    else:
        form = KategoriArtikelForm(instance=kategori)

    context = {
        'title': 'Edit Kategori Artikel',
        'heading': f'Edit Kategori: {kategori.nama_kategori}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'kategori': kategori,
        'is_edit': True,
    }
    return render(request, 'admin_super/kategori_artikel_form.html', context)


@admin_required
def kategori_artikel_hapus(request, id):
    kategori = get_object_or_404(KategoriArtikel, id=id)
    nama = kategori.nama_kategori
    kategori.delete()
    messages.success(request, f'Kategori artikel "{nama}" berhasil dihapus!')
    return redirect('app:kategori_artikel_list')


# ==============================================================================
# CRUD ARTIKEL
# ==============================================================================

@admin_required
def artikel_list(request):
    useradmin, photo = get_admin_data(request)
    artikel_data = Artikel.objects.select_related('kategori', 'penulis').all().order_by('-created_at')

    context = {
        'title': 'Kelola Artikel',
        'heading': 'Daftar Artikel & Panduan Edukasi Kolektor',
        'photo': photo,
        'userdetail': useradmin,
        'artikel_data': artikel_data,
    }
    return render(request, 'admin_super/artikel_list.html', context)


@admin_required
def artikel_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = ArtikelForm(request.POST, request.FILES)
        if form.is_valid():
            art = form.save(commit=False)
            if not art.penulis:
                art.penulis = request.user
            art.save()
            messages.success(request, f'Artikel "{art.judul}" berhasil diterbitkan!')
            return redirect('app:artikel_list')
        else:
            messages.error(request, 'Gagal menerbitkan artikel. Periksa isian form.')
    else:
        form = ArtikelForm()

    context = {
        'title': 'Tambah Artikel',
        'heading': 'Tulis Artikel & Panduan Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/artikel_form.html', context)


@admin_required
def artikel_edit(request, id):
    useradmin, photo = get_admin_data(request)
    artikel = get_object_or_404(Artikel, id=id)

    if request.method == 'POST':
        form = ArtikelForm(request.POST, request.FILES, instance=artikel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Artikel "{artikel.judul}" berhasil diperbarui!')
            return redirect('app:artikel_list')
        else:
            messages.error(request, 'Gagal memperbarui artikel. Periksa isian form.')
    else:
        form = ArtikelForm(instance=artikel)

    context = {
        'title': 'Edit Artikel',
        'heading': f'Edit Artikel: {artikel.judul}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'artikel': artikel,
        'is_edit': True,
    }
    return render(request, 'admin_super/artikel_form.html', context)


@admin_required
def artikel_hapus(request, id):
    artikel = get_object_or_404(Artikel, id=id)
    judul = artikel.judul
    artikel.delete()
    messages.success(request, f'Artikel "{judul}" berhasil dihapus!')
    return redirect('app:artikel_list')


# ==============================================================================
# CRUD HALAMAN
# ==============================================================================

@admin_required
def halaman_list(request):
    useradmin, photo = get_admin_data(request)
    halaman_data = Halaman.objects.all().order_by('-updated_at')

    context = {
        'title': 'Kelola Halaman',
        'heading': 'Daftar Halaman Statis Platform',
        'photo': photo,
        'userdetail': useradmin,
        'halaman_data': halaman_data,
    }
    return render(request, 'admin_super/halaman_list.html', context)


@admin_required
def halaman_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = HalamanForm(request.POST)
        if form.is_valid():
            hal = form.save()
            messages.success(request, f'Halaman "{hal.judul}" berhasil dibuat!')
            return redirect('app:halaman_list')
        else:
            messages.error(request, 'Gagal membuat halaman. Periksa isian form.')
    else:
        form = HalamanForm()

    context = {
        'title': 'Tambah Halaman',
        'heading': 'Tambah Halaman Statis Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/halaman_form.html', context)


@admin_required
def halaman_edit(request, id):
    useradmin, photo = get_admin_data(request)
    halaman = get_object_or_404(Halaman, id=id)

    if request.method == 'POST':
        form = HalamanForm(request.POST, instance=halaman)
        if form.is_valid():
            form.save()
            messages.success(request, f'Halaman "{halaman.judul}" berhasil diperbarui!')
            return redirect('app:halaman_list')
        else:
            messages.error(request, 'Gagal memperbarui halaman. Periksa isian form.')
    else:
        form = HalamanForm(instance=halaman)

    context = {
        'title': 'Edit Halaman',
        'heading': f'Edit Halaman: {halaman.judul}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'halaman': halaman,
        'is_edit': True,
    }
    return render(request, 'admin_super/halaman_form.html', context)


@admin_required
def halaman_hapus(request, id):
    halaman = get_object_or_404(Halaman, id=id)
    judul = halaman.judul
    halaman.delete()
    messages.success(request, f'Halaman "{judul}" berhasil dihapus!')
    return redirect('app:halaman_list')


# ==============================================================================
# CRUD HERO SLIDE
# ==============================================================================

@admin_required
def hero_slide_list(request):
    useradmin, photo = get_admin_data(request)
    slides = HeroSlide.objects.all().order_by('urutan', '-created_at')

    context = {
        'title': 'Hero Slide',
        'heading': 'Kelola Hero Slide Banner Beranda',
        'photo': photo,
        'userdetail': useradmin,
        'slides': slides,
    }
    return render(request, 'admin_super/hero_slide_list.html', context)


@admin_required
def hero_slide_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            slide = form.save()
            messages.success(request, f'Hero slide #{slide.urutan} berhasil ditambahkan!')
            return redirect('app:hero_slide_list')
        else:
            messages.error(request, 'Gagal menambahkan hero slide. Periksa isian form.')
    else:
        form = HeroSlideForm()

    context = {
        'title': 'Tambah Hero Slide',
        'heading': 'Tambah Hero Slide Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/hero_slide_form.html', context)


@admin_required
def hero_slide_edit(request, id):
    useradmin, photo = get_admin_data(request)
    slide = get_object_or_404(HeroSlide, id=id)

    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hero slide #{slide.urutan} berhasil diperbarui!')
            return redirect('app:hero_slide_list')
        else:
            messages.error(request, 'Gagal memperbarui hero slide. Periksa isian form.')
    else:
        form = HeroSlideForm(instance=slide)

    context = {
        'title': 'Edit Hero Slide',
        'heading': f'Edit Hero Slide #{slide.urutan}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'slide': slide,
        'is_edit': True,
    }
    return render(request, 'admin_super/hero_slide_form.html', context)


@admin_required
def hero_slide_hapus(request, id):
    slide = get_object_or_404(HeroSlide, id=id)
    urutan = slide.urutan
    slide.delete()
    messages.success(request, f'Hero slide #{urutan} berhasil dihapus!')
    return redirect('app:hero_slide_list')


# ==============================================================================
# CRUD KERJA SAMA
# ==============================================================================

@admin_required
def kerjasama_list(request):
    useradmin, photo = get_admin_data(request)
    mitra_data = KerjaSama.objects.all().order_by('-created_at')

    context = {
        'title': 'Kerja Sama',
        'heading': 'Kelola Mitra & Ekspedisi Resmi',
        'photo': photo,
        'userdetail': useradmin,
        'mitra_data': mitra_data,
    }
    return render(request, 'admin_super/kerjasama_list.html', context)


@admin_required
def kerjasama_tambah(request):
    useradmin, photo = get_admin_data(request)

    if request.method == 'POST':
        form = KerjaSamaForm(request.POST, request.FILES)
        if form.is_valid():
            mitra = form.save()
            messages.success(request, f'Mitra kerja sama "{mitra.nama_mitra}" berhasil ditambahkan!')
            return redirect('app:kerjasama_list')
        else:
            messages.error(request, 'Gagal menambahkan mitra. Periksa isian form.')
    else:
        form = KerjaSamaForm()

    context = {
        'title': 'Tambah Mitra',
        'heading': 'Tambah Mitra Kerja Sama Baru',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'is_edit': False,
    }
    return render(request, 'admin_super/kerjasama_form.html', context)


@admin_required
def kerjasama_edit(request, id):
    useradmin, photo = get_admin_data(request)
    mitra = get_object_or_404(KerjaSama, id=id)

    if request.method == 'POST':
        form = KerjaSamaForm(request.POST, request.FILES, instance=mitra)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mitra kerja sama "{mitra.nama_mitra}" berhasil diperbarui!')
            return redirect('app:kerjasama_list')
        else:
            messages.error(request, 'Gagal memperbarui mitra. Periksa isian form.')
    else:
        form = KerjaSamaForm(instance=mitra)

    context = {
        'title': 'Edit Mitra',
        'heading': f'Edit Mitra: {mitra.nama_mitra}',
        'photo': photo,
        'userdetail': useradmin,
        'form': form,
        'mitra': mitra,
        'is_edit': True,
    }
    return render(request, 'admin_super/kerjasama_form.html', context)


@admin_required
def kerjasama_hapus(request, id):
    mitra = get_object_or_404(KerjaSama, id=id)
    nama = mitra.nama_mitra
    mitra.delete()
    messages.success(request, f'Mitra "{nama}" berhasil dihapus!')
    return redirect('app:kerjasama_list')


# ==============================================================================
# TRACKING & KELOLA PESANAN (ADMIN)
# ==============================================================================

@admin_required
def pesanan_admin_list(request):
    useradmin, photo = get_admin_data(request)
    status_filter = request.GET.get('status', '').strip()
    search_query = request.GET.get('q', '').strip()

    orders = HistoryPayment.objects.select_related('user_client').prefetch_related('items', 'items__product').order_by('-payment_date')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if search_query:
        orders = orders.filter(
            Q(invoice_number__icontains=search_query) |
            Q(user_client__username__icontains=search_query) |
            Q(shipping_name__icontains=search_query) |
            Q(tracking_number_awb__icontains=search_query) |
            Q(courier_service__icontains=search_query)
        )

    counts = {
        'all': HistoryPayment.objects.count(),
        'pending': HistoryPayment.objects.filter(status='Pending').count(),
        'completed': HistoryPayment.objects.filter(status='Completed').count(),
        'packing': HistoryPayment.objects.filter(status='Packing').count(),
        'shipped': HistoryPayment.objects.filter(status='Shipped').count(),
        'delivered': HistoryPayment.objects.filter(status='Delivered').count(),
        'failed': HistoryPayment.objects.filter(status='Failed').count(),
    }

    context = {
        'title': 'Tracking & Manajemen Pesanan',
        'heading': 'Kelola Pesanan & Resi Pengiriman',
        'photo': photo,
        'userdetail': useradmin,
        'orders': orders,
        'status_filter': status_filter,
        'search_query': search_query,
        'counts': counts,
    }
    return render(request, 'admin_super/pesanan_list.html', context)


@admin_required
def pesanan_admin_detail(request, invoice_number):
    useradmin, photo = get_admin_data(request)
    order = get_object_or_404(
        HistoryPayment.objects.select_related('user_client').prefetch_related('items', 'items__product', 'tracking_logs'),
        invoice_number=invoice_number
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_awb = request.POST.get('tracking_number_awb', '').strip()
        new_courier = request.POST.get('courier_service', '').strip()
        tracking_note = request.POST.get('tracking_note', '').strip()

        old_status = order.status
        old_awb = order.tracking_number_awb

        if new_status:
            order.status = new_status
        if new_awb:
            order.tracking_number_awb = new_awb
        if new_courier:
            order.courier_service = new_courier

        order.save()

        # Otomatis unlock Virtual Binder jika lunas/dikirim
        if new_status in ['Completed', 'Packing', 'Shipped', 'Delivered']:
            order.unlock_virtual_binder()

        # Catat Tracking Log
        log_parts = []
        if old_status != new_status:
            log_parts.append(f"Status diubah ke {order.get_status_display()}")
        if new_awb and new_awb != old_awb:
            log_parts.append(f"No. Resi Kurir: {new_awb}")
        if tracking_note:
            log_parts.append(tracking_note)

        full_note = " — ".join(log_parts) if log_parts else f"Pesanan diproses oleh admin {useradmin.username}."
        OrderTrackingLog.objects.create(
            order=order,
            status=order.status,
            note=full_note
        )

        messages.success(request, f'Status & informasi pelacakan pesanan #{order.invoice_number} berhasil diperbarui!')
        return redirect('app:pesanan_admin_detail', invoice_number=order.invoice_number)

    context = {
        'title': f'Kelola Pesanan #{order.invoice_number}',
        'heading': f'Tracking & Kelola Pesanan #{order.invoice_number}',
        'photo': photo,
        'userdetail': useradmin,
        'order': order,
        'logs': order.tracking_logs.all(),
        'status_choices': HistoryPayment.PAYMENT_STATUS,
    }
    return render(request, 'admin_super/pesanan_detail.html', context)


