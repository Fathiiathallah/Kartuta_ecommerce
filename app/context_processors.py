from .models import WebSetting, Halaman


# ponytail: satu query tambahan per request untuk halaman kebijakan; pindah ke cache kalau traffic naik
def web_setting(request):
    # Hanya tautkan klaim garansi kalau halaman kebijakannya benar-benar ada.
    # Tanpa fallback: lebih baik klaim tampil tanpa tautan daripada menautkan ke halaman yang tidak relevan.
    info_page = Halaman.objects.filter(
        aktif=True, slug__iregex=r'(garansi|refund|kebijakan|syarat)'
    ).order_by('id').first()
    return {
        'web_setting': WebSetting.objects.first(),
        'info_page': info_page,
    }
