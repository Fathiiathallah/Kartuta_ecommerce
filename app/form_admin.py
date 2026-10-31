from django import forms
from .models import UserAdmin, Category, Product

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
