from .models import WebSetting

def web_setting(request):
    return {
        'web_setting': WebSetting.objects.first()
    }
