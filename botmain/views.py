from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from discord_auth_data.models import *
from django.conf import settings
from .templatetags import extras


# Create your views here.
@login_required
def home(request):
    servers = {}
    discord = DiscordUser.objects.values('access_token').filter(user=request.user)

    guilds = requests.get(f'{settings.DISCORD_BASE_URI }/users/@me/guilds', 
    headers={
        'Authorization': f'Bearer {discord[0]["access_token"]}',
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
    return render(request,'home.html',{
        'server_name': 'Server Selection Dashboard',
        'servers':servers
    })

@login_required
def server_inside(request,userid,serverid):
    pass