from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import UserAdmin, UserPengguna, Product, Category


def homeView(request):
    category_id = request.GET.get('category')
    if category_id:
        products = Product.objects.filter(category_id=category_id).select_related('category').order_by('-created_at')
    else:
        products = Product.objects.select_related('category').all().order_by('-created_at')

    categories = Category.objects.all()

    context = {
        'title': 'KartuTa - K-Pop Photocard Official E-Commerce',
        'heading': 'Etalase Official Photocard & Virtual Binder',
        'products': products,
        'categories': categories,
        'active_category': category_id,
    }
    return render(request, 'homepage/index.html', context)


def loginView(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.last_name == 'Super Admin':
            return redirect('app:dashboard_admin')
        return redirect('home')

    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = User.objects.filter(email=login_input).first() or User.objects.filter(username=login_input).first()
        auth_user = authenticate(request, username=user.username, password=password) if user else None

        if auth_user:
            login(request, auth_user)
            messages.success(request, f'Selamat Datang, {auth_user.first_name or auth_user.username}!')
            if auth_user.is_staff or auth_user.last_name == 'Super Admin':
                return redirect('app:dashboard_admin')
            return redirect('home')

        messages.warning(request, 'Email/Username atau password salah.')
        return redirect('login')

    return render(request, 'login.html', {
        'title': 'Login',
        'heading': 'Masuk ke Platform KartuTa',
    })


def registerView(request):
    if request.user.is_authenticated:
        return redirect('app:index')

    if request.method == 'POST':
        name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')

        if confirm != password:
            messages.warning(request, 'Password dan konfirmasi password tidak cocok.')
        elif User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            messages.warning(request, 'Email sudah terdaftar.')
        else:
            new_user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                last_name='Pengguna',
            )
            UserPengguna.objects.create(
                user=new_user,
                username=email,
                email=email,
                membership_tier='Basic'
            )
            messages.success(request, 'Registrasi berhasil, silakan login!')
            return redirect('login')

    return render(request, 'register.html', {
        'title': 'Daftar Akun',
        'heading': 'Pendaftaran Akun Kolektor',
    })


@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Anda telah berhasil logout!')
    return redirect('login')
