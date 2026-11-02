import os
import mimetypes
import urllib.request
import urllib.error
import urllib.parse
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseMediaStorage(Storage):
    def __init__(self, **kwargs):
        self.supabase_url = getattr(settings, 'SUPABASE_URL', 'https://tbdqyckxugzornkzhbgq.supabase.co').rstrip('/')
        self.supabase_key = getattr(settings, 'SUPABASE_KEY', 'sb_publishable_uopLb-jrYVKjsvQTh89Y2w_8DKdw6iq')
        self.bucket = getattr(settings, 'SUPABASE_BUCKET', 'media')
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}"

    def _headers(self, content_type='application/octet-stream'):
        return {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': content_type,
            'x-upsert': 'true',
        }

    def _save(self, name, content):
        clean_name = str(name).replace('\\', '/').lstrip('/')
        encoded_path = urllib.parse.quote(clean_name, safe='/')
        upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{encoded_path}"

        if hasattr(content, 'read'):
            content.seek(0)
            data = content.read()
        else:
            data = bytes(content)

        content_type, _ = mimetypes.guess_type(clean_name)
        if not content_type:
            content_type = 'application/octet-stream'

        req = urllib.request.Request(
            upload_url,
            data=data,
            headers=self._headers(content_type),
            method='POST'
        )

        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            raise IOError(f"Supabase upload error {e.code}: {error_body}")
        except Exception as e:
            raise IOError(f"Supabase connection error: {e}")

        # Local cache backup
        try:
            local_path = os.path.join(settings.MEDIA_ROOT, clean_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(data)
        except Exception:
            pass

        return clean_name

    def _open(self, name, mode='rb'):
        clean_name = str(name).replace('\\', '/').lstrip('/')
        url = self.url(clean_name)
        try:
            req = urllib.request.Request(url, headers={'apikey': self.supabase_key})
            with urllib.request.urlopen(req) as resp:
                return ContentFile(resp.read(), name=clean_name)
        except Exception as e:
            raise IOError(f"Unable to read file from Supabase: {e}")

    def exists(self, name):
        return False

    def url(self, name):
        if not name:
            return ''
        clean_name = str(name).replace('\\', '/').lstrip('/')
        if clean_name.startswith('http://') or clean_name.startswith('https://'):
            return clean_name
        encoded_path = urllib.parse.quote(clean_name, safe='/')
        return f"{self.base_url}/{encoded_path}"

    def delete(self, name):
        clean_name = str(name).replace('\\', '/').lstrip('/')
        encoded_path = urllib.parse.quote(clean_name, safe='/')
        delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{encoded_path}"
        req = urllib.request.Request(
            delete_url,
            headers=self._headers(),
            method='DELETE'
        )
        try:
            urllib.request.urlopen(req)
        except Exception:
            pass

        local_path = os.path.join(settings.MEDIA_ROOT, clean_name)
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except Exception:
                pass

