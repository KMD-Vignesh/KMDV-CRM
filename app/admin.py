from django.contrib import admin

from .models import (
    Category,
    Inventory,
    Order,
    Product,
    PurchaseOrder,
    UserProfile,
    Vendor,
)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(UserProfile)
admin.site.register(PurchaseOrder)
