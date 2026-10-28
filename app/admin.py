from django.contrib import admin
from .models import (
    UserAdmin, UserClient, Category,
    MediaGambarProduk, Product, HistoryPayment, VirtualBinder
)

admin.site.register(UserAdmin)
admin.site.register(UserClient)
admin.site.register(Category)
admin.site.register(MediaGambarProduk)
admin.site.register(Product)
admin.site.register(HistoryPayment)
admin.site.register(VirtualBinder)