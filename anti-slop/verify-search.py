
import os, sys, django
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.test import Client
from app.models import Product

c = Client()
p = Product.objects.first()
print('produk contoh:', p.name, '| fandom:', p.fandom_group)

# 1. form pencarian ada dan bukan anchor
home = c.get('/home/').content.decode()
print('form role=search:', 'role="search"' in home)
print('input name=q:', 'name="q"' in home)
print('readonly hilang:', 'readonly' not in home.split('nav-search-wrap')[1][:800])

# 2. pencarian benar-benar menyaring
key = p.name.split()[0]
r = c.get('/home/', {'q': key})
print(f'query "{key}" status:', r.status_code, '| jumlah kartu:', r.content.decode().count('pro-card-image-wrapper'))

# 3. query tanpa hasil -> empty state khusus pencarian
r0 = c.get('/home/', {'q': 'zzzTidakAda999'})
body = r0.content.decode()
print('empty state pencarian:', 'Tidak ada photocard yang cocok' in body)

# 4. query nyasar ke kategori tetap jalan
cat = Product.objects.first().category
r2 = c.get('/home/', {'category': cat.id})
print('kategori filter:', r2.status_code)

# 5. nilai q terisi balik di input
rq = c.get('/home/', {'q': key})
print('input value terisi:', f'value="{key}"' in rq.content.decode())
