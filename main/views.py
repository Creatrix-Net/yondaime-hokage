from django.shortcuts import render
from django.http import HttpResponse
from login.bot_ipc_connect import BotIPCConnect

#get_bot_pfp

# Create your views here.

async def home(request):
    a=BotIPCConnect()
    return render(
        request,
        'index.html',
        {
            'bot_pfp': await a.get_pfp(),
        }
    )