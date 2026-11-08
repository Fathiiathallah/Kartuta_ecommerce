from django.contrib import admin
from .models import (
    UserAdmin, UserClient, Category,
    MediaGambarProduk, Product, HistoryPayment, VirtualBinder,
    KategoriArtikel, Artikel, Halaman, HeroSlide, KerjaSama
)

admin.site.register(UserAdmin)
admin.site.register(UserClient)
admin.site.register(Category)
admin.site.register(MediaGambarProduk)
admin.site.register(Product)
admin.site.register(HistoryPayment)
admin.site.register(VirtualBinder)

# ARTIKEL & HALAMAN
@admin.register(KategoriArtikel)
class KategoriArtikelAdmin(admin.ModelAdmin):
    list_display = ('nama_kategori', 'slug', 'aktif', 'created_at')
    prepopulated_fields = {'slug': ('nama_kategori',)}
    search_fields = ('nama_kategori',)

@admin.register(Artikel)
class ArtikelAdmin(admin.ModelAdmin):
    list_display = ('judul', 'kategori', 'penulis', 'is_published', 'created_at')
    list_filter = ('kategori', 'is_published', 'created_at')
    search_fields = ('judul', 'konten')
    prepopulated_fields = {'slug': ('judul',)}

@admin.register(Halaman)
class HalamanAdmin(admin.ModelAdmin):
    list_display = ('judul', 'slug', 'aktif', 'updated_at')
    prepopulated_fields = {'slug': ('judul',)}
    search_fields = ('judul', 'konten')

# TAMPILAN & MITRA
@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('judul', 'urutan', 'badge_text', 'aktif', 'created_at')
    list_editable = ('urutan', 'aktif')
    search_fields = ('judul', 'subjudul')

@admin.register(KerjaSama)
class KerjaSamaAdmin(admin.ModelAdmin):
    list_display = ('nama_mitra', 'kategori_mitra', 'aktif', 'created_at')
    search_fields = ('nama_mitra', 'deskripsi')
