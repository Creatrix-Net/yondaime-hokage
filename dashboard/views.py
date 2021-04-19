from django.shortcuts import render
from discord_auth_data.bot_ipc_connect import BotIPCConnect
from django.conf import settings
from discord_auth_data.decorators import myuser_login_required
from django.http import HttpResponseRedirect


# Create your views here.
def logout(request):
    try:
        del request.session[str(request.session.session_key)]
    except: pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@myuser_login_required
async def announcements(request,id):
    a=BotIPCConnect()
    return render(request,'announcements.html',{
        'server_name': 'Announcement Portal',
        'docs':settings.DOCS,
        'website':settings.WEBSITE,
        'textchannel': await a.ipc_client.request("get_text_channels", guildid=id)
    })