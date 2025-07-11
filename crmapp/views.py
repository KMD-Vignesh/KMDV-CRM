from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the crm index now")

def product(request):
    return HttpResponse("Hello, world. You're at the crm product now")