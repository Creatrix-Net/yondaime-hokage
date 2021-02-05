from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from discord_auth_data.models import *
from django.conf import settings
from .templatetags import extras
import requests


# Create your views here.
@login_required
def home(request):
    servers = {}
    discord = DiscordUser.objects.values('access_token','uid').filter(user=request.user).get()

    guilds = requests.get(f'{settings.DISCORD_BASE_URI }/users/@me/guilds', 
    headers={
        'Authorization': f'Bearer {discord["access_token"]}',
    })
    for i in guilds.json():
        b=requests.get(
            f'{settings.DISCORD_BASE_URI }/guilds/{i["id"]}/members',
        headers={
            'Authorization': f'Bot {settings.BOT_ID}'
        }
        )
        if b.status_code == 200:
            servers[i["name"]] = i
    
    userid = discord['uid']
    request.session['server'] = servers
    return render(request,'home.html',{
        'server_name': 'Server Selection Dashboard',
        'servers':servers,
        'userid':userid
    })

@login_required
def server_inside(request,userid,serverid):
    servers = request.session.get('server',False)
    if not servers:
        return HttpResponseRedirect(reverse('Home'))
    for i in servers:
        if servers[i]['id'] == serverid:
            name= i
            server_dict = servers[i]
            for i in server_dict:
                server_dict[i] = str(server_dict[i])
    
    discord = DiscordUser.objects.values('access_token','uid').filter(user=request.user).get()

    guilds = requests.get(f'{settings.DISCORD_BASE_URI }/guilds/{serverid}/members',headers=server_dict)
    print(guilds, guilds.json())
    return render(
        request,
        'server-members.html',
        {
            'server_name': name,
        }
    )

def keep_alive(request):
    return render(
        request, 
        'keep_alive.html',
        {
            'server_name': 'Keeping Alive The Bot',
        }
    )

def invite_bot(request):
    from requests_oauthlib import OAuth2Session
    return OAuth2Session(
        client_id=settings.DISCORD_CLIENT_ID,
        permissions=8,
        auto_refresh_kwargs={
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
        },
        scope=['bot',],
    )