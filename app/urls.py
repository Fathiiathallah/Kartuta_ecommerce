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

    # ARTIKEL & HALAMAN CRUD
    path('artikel/', views_admin.artikel_list, name='artikel_list'),
    path('artikel/tambah/', views_admin.artikel_tambah, name='artikel_tambah'),
    path('artikel/edit/<int:id>/', views_admin.artikel_edit, name='artikel_edit'),
    path('artikel/hapus/<int:id>/', views_admin.artikel_hapus, name='artikel_hapus'),

    path('kategori-artikel/', views_admin.kategori_artikel_list, name='kategori_artikel_list'),
    path('kategori-artikel/tambah/', views_admin.kategori_artikel_tambah, name='kategori_artikel_tambah'),
    path('kategori-artikel/edit/<int:id>/', views_admin.kategori_artikel_edit, name='kategori_artikel_edit'),
    path('kategori-artikel/hapus/<int:id>/', views_admin.kategori_artikel_hapus, name='kategori_artikel_hapus'),

    path('halaman/', views_admin.halaman_list, name='halaman_list'),
    path('halaman/tambah/', views_admin.halaman_tambah, name='halaman_tambah'),
    path('halaman/edit/<int:id>/', views_admin.halaman_edit, name='halaman_edit'),
    path('halaman/hapus/<int:id>/', views_admin.halaman_hapus, name='halaman_hapus'),

    # TAMPILAN & MITRA CRUD
    path('hero-slide/', views_admin.hero_slide_list, name='hero_slide_list'),
    path('hero-slide/tambah/', views_admin.hero_slide_tambah, name='hero_slide_tambah'),
    path('hero-slide/edit/<int:id>/', views_admin.hero_slide_edit, name='hero_slide_edit'),
    path('hero-slide/hapus/<int:id>/', views_admin.hero_slide_hapus, name='hero_slide_hapus'),

    path('kerjasama/', views_admin.kerjasama_list, name='kerjasama_list'),
    path('kerjasama/tambah/', views_admin.kerjasama_tambah, name='kerjasama_tambah'),
    path('kerjasama/edit/<int:id>/', views_admin.kerjasama_edit, name='kerjasama_edit'),
    path('kerjasama/hapus/<int:id>/', views_admin.kerjasama_hapus, name='kerjasama_hapus'),

    ###### PENGGUNA/CLIENTS ######
    path('profile/pengguna', views_pengguna.profile_pengguna, name='profile_pengguna'),
    path('dashboard/pengguna', views_pengguna.dashboard_pengguna, name='dashboard_pengguna'),
    path('katalog/', views_pengguna.katalog_pengguna, name='katalog_pengguna'),

    ###### UMUM ######
    path('dashboard', views.index, name='dashboard'),
    path('', views.index, name='index'),
]
