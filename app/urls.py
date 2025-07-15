from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/add/', views.add_vendor, name='add_vendor'),
    path('vendors/edit/<int:pk>/', views.edit_vendor, name='edit_vendor'),
    path('vendors/delete/<int:pk>/', views.delete_vendor, name='delete_vendor'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.add_inventory, name='add_inventory'),
    path('inventory/edit/<int:pk>/', views.edit_inventory, name='edit_inventory'),
    path('inventory/delete/<int:pk>/', views.delete_inventory, name='delete_inventory'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/add/', views.add_order, name='add_order'),
    path('orders/edit/<int:pk>/', views.edit_order, name='edit_order'),
    path('orders/cancel/<int:pk>/', views.cancel_order, name='cancel_order'),
    path('register/', views.register, name='register'),  
    path('profile/', view=views.profile, name='profile'),
    path('load-vendors/', views.load_vendors, name='load_vendors'),
    path('get-stock-quantity/', views.get_stock_quantity, name='get_stock_quantity'),

]