from django.urls import path
from . import views
from . import views_admin
from . import views_pengguna

urlpatterns = [
    ###### ADMIN ######
    path('profile/admin', views_admin.profile_admin, name='profile_admin'),
    path('dashboard/admin', views_admin.dashboard_admin, name='dashboard_admin'),
    
    # Kategori CRUD
    path('kategori/', views_admin.kategori_list, name='kategori_list'),
    path('kategori/tambah/', views_admin.kategori_tambah, name='kategori_tambah'),
    path('kategori/edit/<int:id>/', views_admin.kategori_edit, name='kategori_edit'),
    path('kategori/hapus/<int:id>/', views_admin.kategori_hapus, name='kategori_hapus'),

    # Produk CRUD
    path('produk/', views_admin.produk_list, name='produk_list'),
    path('produk/tambah/', views_admin.produk_tambah, name='produk_tambah'),
    path('produk/edit/<int:id>/', views_admin.produk_edit, name='produk_edit'),
    path('produk/hapus/<int:id>/', views_admin.produk_hapus, name='produk_hapus'),

    ###### PENGGUNA/CLIENTS ######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),
    path('dashboard/pengguna', views_pengguna.dashboard_pengguna, name='dashboard_pengguna'),
    path('katalog/', views_pengguna.katalog_pengguna, name='katalog_pengguna'),

    ###### UMUM ######
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),
]
