from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render


def keep_alive(request):
    return HttpResponse('<a href="https://discordbotlist.com/bots/779559821162315787"><img src="https://discordbotlist.com/api/v1/bots/779559821162315787/widget"></a>')
