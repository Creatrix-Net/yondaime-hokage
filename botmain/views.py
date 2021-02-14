from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.conf import settings
from django.urls import reverse


# Create your views here.
def home(request):
    return redirect(reverse('admin:index'))

def home_view_alive(request):
    return HttpResponse('<h1>Congratulations You succesfully kept the bot alive</h1>', status=200)
