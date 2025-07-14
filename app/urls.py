from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("product", view=views.product, name="product"),
    path("category", view=views.category, name="category"),
    path("user", view=views.user, name="user"),
    path("order", view=views.order, name="order"),

]
