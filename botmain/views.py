from django.contrib import messages
import requests

from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.conf import settings

from .models import *
from django.conf import settings
from discord_auth_data.bot_ipc_connect import BotIPCConnect

# Create your views here.
async def main(request):
    a=BotIPCConnect()
    return render(
        request,
        'index.html',
        {
            'bot_pfp': await a.ipc_client.request("get_bot_pfp"),
        }
    )


def keep_alive(request):
    if request.META.get('HTTP_AUTHORIZATION') == settings.AUTH_PASS:
        return render(
            request, 
            'keep_alive.html',
            {
                'server_name': 'Keeping Alive The Bot',
                'docs':settings.DOCS,
                'website':settings.WEBSITE,
            }
        )
    else:
        return redirect(reverse('Home'))

def invite_bot(request):
    return redirect('https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&scope=bot%20applications.commands')


def return_available_anime(request, name):
    name_id = AnimeName.objects.filter(anime_name__in=name).all()
    anime = [i.anime_name for i in AnimeName.objects.iterator()]
