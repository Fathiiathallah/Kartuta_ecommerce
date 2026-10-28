from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserAdmin, UserPengguna, Product, Category, HistoryPayment, VirtualBinder

@login_required
def index(request):
    today = timezone.localdate()

    if request.user.last_name == 'Super Admin' or request.user.is_staff or request.user.is_superuser:
        userC = (
            UserAdmin.objects.filter(user=request.user).first() or
            UserAdmin.objects.filter(username=request.user.username).first() or
            UserAdmin.objects.filter(email=request.user.email).first()
        )
        if userC and not userC.user:
            userC.user = request.user
            userC.save()
        elif not userC:
            userC = UserAdmin.objects.create(
                user=request.user,
                username=request.user.username,
                email=request.user.email or f"{request.user.username}@kartuta.id",
                role_divisi='Operations & QC'
            )

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
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'stats': stats,
            'clients': clients,
            'today': today,
        }
        return render(request, 'admin_super/index.html', context)

    else:
        userC = UserPengguna.objects.filter(user=request.user).first()
        if not userC:
            userC = UserPengguna.objects.filter(username=request.user.username).first()

        if not userC:
            messages.error(request, 'Profil pengguna belum tersedia.')
            return redirect('app:profile_pengguna')

        if not userC.telp or not userC.alamat:
            messages.warning(request, 'Harap lengkapi nomor telepon dan alamat pengiriman Anda terlebih dahulu.')
            return redirect('app:profile_pengguna')

        binders = VirtualBinder.objects.filter(user_client=userC)
        payments = HistoryPayment.objects.filter(user_client=userC).order_by('-payment_date')

        context = {
            'title': 'Dashboard',
            'heading': 'Dashboard Pengguna',
            'photo': userC.photo if userC and userC.photo else None,
            'userdetail': userC,
            'binders': binders,
            'payments': payments,
            'today': today,
        }
        return render(request, 'pengguna/index.html', context)
