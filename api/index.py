"""Entri serverless untuk preset Django di Vercel.

Preset Django mencari variabel `app` di `core/wsgi.py`, tapi sebagian deployment
memakai `api/index.py`. File ini menyediakan keduanya tanpa mengubah struktur proyek.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from core.wsgi import application  # noqa: E402

handler = application
app = application
