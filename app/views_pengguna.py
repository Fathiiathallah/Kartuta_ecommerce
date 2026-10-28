from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .form_pengguna import formProfile
from .models import UserPengguna, VirtualBinder, HistoryPayment
from .decorators_admin import pengguna_required

@login_required
@pengguna_required
def profile_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if not userpengguna:
        userpengguna = UserPengguna.objects.filter(username=request.user.username).first()
        if userpengguna and not userpengguna.user:
            userpengguna.user = request.user
            userpengguna.save()
        elif not userpengguna:
            userpengguna = UserPengguna.objects.create(
                user=request.user,
                username=request.user.username,
                email=request.user.email or request.user.username
            )

    if request.method == 'POST':
        form = formProfile(request.POST, request.FILES, instance=userpengguna)
        if form.is_valid():
            pengguna = form.save(commit=False)
            pengguna.user = request.user
            pengguna.save()
            messages.success(request, 'Data profil pengguna berhasil disimpan!')
            return redirect('app:profile_pengguna')
        else:
            messages.error(request, 'Data profil belum lengkap atau terjadi kesalahan pengisian. Silakan periksa kembali.')
    else:
        form = formProfile(instance=userpengguna)

    context = {
        'title': 'Profil Pengguna',
        'heading': 'Profil Kolektor KartuTa',
        'userpengguna': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'form': form,
    }
    return render(request, 'pengguna/profil_pengguna.html', context)


@login_required
@pengguna_required
def dashboard_pengguna(request):
    userpengguna = UserPengguna.objects.filter(user=request.user).first()
    if not userpengguna:
        userpengguna = UserPengguna.objects.filter(username=request.user.username).first()

    binders = VirtualBinder.objects.filter(user_client=userpengguna) if userpengguna else []
    payments = HistoryPayment.objects.filter(user_client=userpengguna).order_by('-payment_date') if userpengguna else []

    context = {
        'title': 'Dashboard',
        'heading': 'Dashboard Pengguna',
        'userdetail': userpengguna,
        'photo': userpengguna.photo if userpengguna and userpengguna.photo else None,
        'binders': binders,
        'payments': payments,
    }
    return render(request, 'pengguna/index.html', context)
