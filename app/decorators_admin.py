from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserAdmin, UserPengguna

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.last_name == 'Super Admin' or request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Akses khusus administrator / staf internal!')
        return redirect('app:dashboard')
    return _wrapped_view

def pengguna_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.last_name != 'Super Admin' and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        return redirect('app:dashboard')
    return _wrapped_view

def check_useradmin(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        useradmin = UserAdmin.objects.filter(user=request.user).first()
        if not useradmin:
            useradmin = UserAdmin.objects.filter(username=request.user.username).first()
        request.useradmin = useradmin
        if useradmin and not useradmin.photo:
            messages.warning(request, 'Lengkapi data profil dan foto Anda!')
            return redirect('app:profile_admin')
        return function(request, *args, **kwargs)
    return wrapper

def check_userpengguna(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        userpengguna = UserPengguna.objects.filter(user=request.user).first()
        if not userpengguna:
            userpengguna = UserPengguna.objects.filter(username=request.user.username).first()
        request.userpengguna = userpengguna
        if not userpengguna or not userpengguna.telp or not userpengguna.alamat:
            messages.warning(request, 'Lengkapi nomor telepon dan alamat pengiriman Anda terlebih dahulu!')
            return redirect('app:profile_pengguna')
        return function(request, *args, **kwargs)
    return wrapper
