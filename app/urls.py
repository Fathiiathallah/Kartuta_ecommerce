from django.urls import path
from . import views
from . import views_admin
from . import views_pengguna

urlpatterns = [
    ###### ADMIN ######
    path('profile/admin', views_admin.profile_admin, name='profile_admin'),
    path('dashboard/admin', views_admin.dashboard_admin, name='dashboard_admin'),

    ###### PENGGUNA/CLIENTS ######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),
    path('dashboard/pengguna', views_pengguna.dashboard_pengguna, name='dashboard_pengguna'),

    ###### UMUM ######
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),
]
