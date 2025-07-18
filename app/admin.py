from django.contrib import admin
from .models import (
    Category, Product, Vendor, Inventory,
    Order, UserProfile, PurchaseOrder
)

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Vendor)         
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(UserProfile)
admin.site.register(PurchaseOrder)   