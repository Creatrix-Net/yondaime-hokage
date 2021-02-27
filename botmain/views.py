from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from discord_auth_data.models import *
from django.conf import settings
import discord
from discord import Webhook, RequestsWebhookAdapter

from .models import Webhooks
from django.conf import settings

# Create your views here.
@login_required
def home(request):
    return render(request,'home.html',{
        'server_name': 'Announcement Portal',
        'weebhook': Webhooks.objects.all(),
        'docs':settings.DOCS,
        'website':settings.WEBSITE
    })


def sendmessages(request):
    if request.method == 'POST':
        weebhook = request.POST.get('weebhook')
        announcement = request.POST.get('announcement')
        wbhk_obj = Webhooks.objects.filter(name=weebhook).all()[0]

        webhook = Webhook.partial(wbhk_obj.weebhook_id, wbhk_obj.webhook_token, adapter=RequestsWebhookAdapter())
        e = discord.Embed(title='A message from my developer',description=announcement)
        webhook.send(embed=e)
        messages.success(request,f'Announcement Sent to {weebhook} !')
    return redirect(reverse('Home'))


def keep_alive(request):
    return render(
        request, 
        'keep_alive.html',
        {
            'server_name': 'Keeping Alive The Bot',
            'docs':settings.DOCS,
            'website':settings.WEBSITE
        }
    )

def invite_bot(request):
    from requests_oauthlib import OAuth2Session
    a = OAuth2Session(
        client_id=settings.DISCORD_CLIENT_ID,
        auto_refresh_kwargs={
            'client_id': settings.DISCORD_CLIENT_ID,
            'client_secret': settings.DISCORD_CLIENT_SECRET,
            'permissions': 2147483656
        },
        redirect_uri= request.META.get('HTTP_REFERER'),
        scope=['bot',],
    )
    url, state = a.authorization_url(settings.DISCORD_BASE_URI + settings.DISCORD_AUTHZ_PATH)
    return redirect(url)
