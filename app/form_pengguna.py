from django import forms
from .models import UserPengguna, Provinsi

class formProfile(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[
            ('', '-- Pilih Jenis Kelamin --'),
            ('Laki-laki', 'Laki-laki'),
            ('Perempuan', 'Perempuan'),
        ],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_gender'}),
        required=False
    )

    provinsi_anggota = forms.ModelChoiceField(
        queryset=Provinsi.objects.filter(aktif=True).order_by('nama_provinsi'),
        empty_label='-- Pilih Provinsi Domisili / Pengiriman --',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_provinsi_anggota'}),
        required=False
    )

    class Meta:
        model = UserPengguna
        fields = [
            'telp',
            'gender',
            'alamat',
            'provinsi_anggota',
            'membership_tier',
            'photo',
        ]
        widgets = {
            'telp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 081234567890'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat lengkap pengiriman paket (Jalan, Kota, Kode Pos)'}),
            'membership_tier': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
