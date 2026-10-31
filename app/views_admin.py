from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserAdmin, UserPengguna, Product, Category, HistoryPayment
from .form_admin import formProfile, CategoryForm, ProductForm
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
