from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.index, name="index"),
    path("product", view=views.product, name="product"),

]