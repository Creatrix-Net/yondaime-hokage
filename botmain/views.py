from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from django.conf import settings
from django.urls import reverse


# Create your views here.
def home(request):
    return redirect(reverse('admin:index'))

def home_view_alive(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    token_type, _, credentials = auth_header.partition(' ')
    import base64
    data = f'{settings.ID}:{settings.SECRECT}'
    expected = data
    if token_type != 'Basic' or credentials != expected:
        return HttpResponse(status=401)
    else:
        return HttpResponse('<h1>Congratulations You succesfully kept the bot alive</h1>')
