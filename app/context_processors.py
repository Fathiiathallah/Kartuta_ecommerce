from django.db.models import Sum
from .models import WebSetting, CartItem

def web_setting(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    return {
        'web_setting': WebSetting.objects.first(),
        'cart_count': cart_count,
    }
