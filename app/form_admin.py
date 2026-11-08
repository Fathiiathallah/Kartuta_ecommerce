from django import forms
from .models import (
    UserAdmin, Category, Product,
    KategoriArtikel, Artikel, Halaman, HeroSlide, KerjaSama
)

class formProfile(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jenis Kelamin --'),
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    role_divisi = forms.ChoiceField(
        choices=[
            ('Operations & QC', 'Operations & QC (Card Grading)'),
            ('Inventory & Packing', 'Inventory & Packing (4-Layer Safety)'),
            ('Customer Support', 'Customer Support & Community'),
            ('Super Admin', 'Super Admin'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    class Meta:
        model = UserAdmin
        fields = [
            'telp',
            'gender',
            'role_divisi',
            'photo',
        ]
        widgets = {
            'telp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor kontak staf'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Kategori (Contoh: aespa Armageddon)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi singkat kategori photocard'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

formKategori = CategoryForm


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'fandom_group',
            'member_bias',
            'category',
            'price',
            'stock',
            'card_grade',
            'description',
            'image_utama',
            'is_official_verified',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Photocard (Contoh: Karina Supernova Hologram)'}),
            'fandom_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grup (aespa, NewJeans, IVE, dll)'}),
            'member_bias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Member (Karina, Winter, Hanni, Wonyoung)'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Harga satuan (Rp)'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah stok tersedia'}),
            'card_grade': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detail kondisi kartu, cetakan album, atau event benefit'}),
            'image_utama': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_official_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

formProduk = ProductForm


class KategoriArtikelForm(forms.ModelForm):
    class Meta:
        model = KategoriArtikel
        fields = ['nama_kategori', 'deskripsi', 'aktif']
        widgets = {
            'nama_kategori': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Kategori (Contoh: Panduan Kolektor)'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi singkat kategori artikel'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ArtikelForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = ['judul', 'kategori', 'konten', 'gambar_utama', 'is_published']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul Artikel / Panduan Edukasi'}),
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'konten': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Isi artikel lengkap...'}),
            'gambar_utama': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HalamanForm(forms.ModelForm):
    class Meta:
        model = Halaman
        fields = ['judul', 'slug', 'konten', 'aktif']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul Halaman (Contoh: Tentang Kami / Kebijakan Privasi)'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Slug URL (Opsional, otomatis dibuat jika kosong)'}),
            'konten': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Isi teks halaman statis...'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ['judul', 'subjudul', 'badge_text', 'gambar', 'link_url', 'tombol_teks', 'urutan', 'aktif']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Judul Banner Slide (Mendukung tag HTML sederhana)'}),
            'subjudul': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deskripsi / Subjudul slide'}),
            'badge_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teks Badge (Contoh: OFFICIAL COMEBACK DROP)'}),
            'gambar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link Tujuan (Contoh: #katalog-etalase atau /home/)'}),
            'tombol_teks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Label Tombol (Contoh: Jelajahi Etalase ↓)'}),
            'urutan': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nomor Urutan (1, 2, 3...)'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class KerjaSamaForm(forms.ModelForm):
    class Meta:
        model = KerjaSama
        fields = ['nama_mitra', 'kategori_mitra', 'logo', 'link_url', 'deskripsi', 'aktif']
        widgets = {
            'nama_mitra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Instansi / Mitra (Contoh: J&T Express Official)'}),
            'kategori_mitra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kategori (Ekspedisi Logistik, Payment, dll)'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'link_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Website / Profil Mitra'}),
            'deskripsi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Deskripsi singkat kerja sama'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

