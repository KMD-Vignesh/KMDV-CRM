from django.contrib import admin

from .models import Category, Inventory, Order, Product, UserProfile

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(UserProfile)
