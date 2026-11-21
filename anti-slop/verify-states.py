
import os, sys, django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User

# DEBUG=False supaya handler 404/500 custom yang dipakai
with override_settings(DEBUG=False):
    c = Client()
    r = c.get('/halaman/tidak-ada-sama-sekali/')
    print('404 status:', r.status_code)
    body = r.content.decode()
    print('404 template custom:', 'tidak ada di arsip' in body)
    print('404 lang attr:', '<html lang="id">' in body)

    r500 = c.get('/halaman/tidak-ada-sama-sekali/')
    print('404 has etalase link:', 'Kembali ke etalase' in body)

# loading script di halaman yang extends base
admin = User.objects.filter(is_staff=True).first()
c2 = Client(); c2.force_login(admin)
res = c2.get('/app/dashboard/admin')
html = res.content.decode()
print('dashboard status:', res.status_code)
print('loading script present:', 'Memproses' in html)
