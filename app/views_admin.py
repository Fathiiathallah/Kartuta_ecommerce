from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserAdmin, UserPengguna, Product, Category, HistoryPayment
from .form_admin import formProfile
from .decorators_admin import admin_required

@admin_required
def profile_admin(request):
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
        'photo': useradmin.photo if useradmin and useradmin.photo else None,
        'form': form,
    }
    return render(request, 'admin_super/profile_admin.html', context)


@admin_required
def dashboard_admin(request):
    useradmin = UserAdmin.objects.filter(user=request.user).first()
    if not useradmin:
        useradmin = UserAdmin.objects.filter(username=request.user.username).first()

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
        'photo': useradmin.photo if useradmin and useradmin.photo else None,
        'userdetail': useradmin,
        'stats': stats,
        'clients': clients,
    }
    return render(request, 'admin_super/index.html', context)
