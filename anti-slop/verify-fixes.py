
import os, sys, django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.test import Client
from app.models import Artikel, Halaman, HistoryPayment, Product

c = Client()

# 1. halaman utama & detail
checks = []
for url in ['/home/', '/produk/2/', f'/artikel/{Artikel.objects.filter(is_published=True).first().slug}/']:
    checks.append((url, c.get(url).status_code))

# 2. 404 handler
r = c.get('/halaman/tidak-ada-sama-sekali/')
checks.append(('404 custom', r.status_code))

# 3. loading state script ada di halaman dashboard (extends base)
admin_res = c.get('/login/')
checks.append(('login page', admin_res.status_code))

for u, s in checks:
    print(f'{s}  {u}')

# 4. fokus ring + reduced motion ada di CSS
css = open('static/css/style.css', encoding='utf-8').read()
print('focus-visible rules:', css.count(':focus-visible'))
print('prefers-reduced-motion:', 'prefers-reduced-motion' in css)
print('real search form:', 'role="search"' in c.get('/home/').content.decode())

# 5. tidak ada input readonly palsu
home = c.get('/home/').content.decode()
print('readonly search gone:', 'readonly onclick' not in home)
print('announcement claim span fallback:', 'announcement-claim' not in home)

# 6. em dash bersih
import glob
bad = []
for f in glob.glob('templates/**/*.html', recursive=True):
    if chr(8212) in open(f, encoding='utf-8').read():
        bad.append(f)
print('em dash files:', bad)
print('64748B remaining:', sum(open(f, encoding='utf-8').read().count('64748') for f in glob.glob('templates/**/*.html', recursive=True)))
