from django.http import HttpResponse
from django.shortcuts import render  # noqa: F401


def index(request):
    return HttpResponse("Hello, world. You're at the crm index now")


def product(request):
    return HttpResponse("Hello, world. You're at the crm product now")

def category(request):
    return HttpResponse("Hello, world. You're at the crm category now")

def user(request):
    return HttpResponse("Hello, world. You're at the crm user now")

def order(request):
    return HttpResponse("Hello, world. You're at the crm order now")
