from django import forms
from .models import UserAdmin

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
