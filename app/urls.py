from django.urls import path

from . import views
from .view import category_view, product_view, vendor_view, inventory_view, order_view, user_view, purchase_view, approval_view


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("products/", product_view.product_list, name="product_list"),
    path("products/add/", product_view.add_product, name="add_product"),
    path("products/edit/<int:pk>/", product_view.edit_product, name="edit_product"),
    path("products/delete/<int:pk>/", product_view.delete_product, name="delete_product"),
    path("categories/", category_view.category_list, name="category_list"),
    path("categories/add/", category_view.add_category, name="add_category"),
    path("categories/edit/<int:pk>/", category_view.edit_category, name="edit_category"),
    path("categories/delete/<int:pk>/", category_view.delete_category, name="delete_category"),
    path("vendors/", vendor_view.vendor_list, name="vendor_list"),
    path("vendors/add/", vendor_view.add_vendor, name="add_vendor"),
    path("vendors/edit/<int:pk>/", vendor_view.edit_vendor, name="edit_vendor"),
    path("vendors/delete/<int:pk>/", vendor_view.delete_vendor, name="delete_vendor"),
    path("inventory/", inventory_view.inventory_list, name="inventory_list"),
    path("inventory/add/", inventory_view.add_inventory, name="add_inventory"),
    path("inventory/edit/<int:pk>/", inventory_view.edit_inventory, name="edit_inventory"),
    path("inventory/delete/<int:pk>/", inventory_view.delete_inventory, name="delete_inventory"),
    path("orders/", order_view.order_list, name="order_list"),
    path("orders/add/", order_view.add_order, name="add_order"),
    path("load-vendors/", order_view.load_vendors, name="load_vendors"),
    path("get-stock-quantity/", order_view.get_stock_quantity, name="get_stock_quantity"),
    path("orders/edit/<int:pk>/", order_view.edit_order, name="edit_order"),
    path("orders/cancel/<int:pk>/", order_view.cancel_order, name="cancel_order"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path('accounts/',        user_view.user_list,   name='user_list'),
    path('accounts/add/',    user_view.user_add,    name='user_add'),
    path('accounts/<int:pk>/edit/',   user_view.user_edit,   name='user_edit'),
    path('accounts/<int:pk>/delete/', user_view.user_delete, name='user_delete'),
    path('accounts/<int:pk>/reset-password/', user_view.user_reset_password, name='user_reset_password'),
    path('purchase/',          purchase_view.purchase_list,   name='purchase_list'),
    path('purchase/add/',      purchase_view.add_purchase,    name='add_purchase'),
    path('purchase/<int:pk>/edit/', purchase_view.edit_purchase, name='edit_purchase'),
    path('purchase/<int:pk>/delete/', purchase_view.delete_purchase, name='delete_purchase'),
    path('purchase/<int:pk>/print/', purchase_view.print_purchase_order, name='print_purchase_order'),
    path('approval-request/', approval_view.approval_request_list, name='approval_request_list'),
    path('approval-manager/', approval_view.approval_manager_list, name='approval_manager_list'),
    path('approve-purchase-order/<int:pk>/', approval_view.approve_purchase_order, name='approve_purchase_order'),
    path('cancel-purchase-order/<int:pk>/', approval_view.reject_purchase_order, name='reject_purchase_order'),
    path('approval-request-detail/<int:pk>/', approval_view.approval_request_detail, name='approval_request_detail'), 

]
