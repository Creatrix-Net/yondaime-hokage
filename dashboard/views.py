from django.shortcuts import render
from discord_auth_data.bot_ipc_connect import BotIPCConnect
from django.conf import settings
from discord_auth_data.decorators import myuser_login_required, myuser_manage_server_perms
from django.http import HttpResponseRedirect


# Create your views here.

@myuser_login_required
@myuser_manage_server_perms
async def announcements(request,userid,serverid):
    a=BotIPCConnect()
    return render(request,'announcements.html',{
        'server_name': 'Announcement Portal',
        'docs':settings.DOCS,
        'website':settings.WEBSITE,
        'textchannel': await a.ipc_client.request("get_text_channels", guildid=serverid)
    })