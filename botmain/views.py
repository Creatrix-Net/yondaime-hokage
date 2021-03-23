from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from discord_auth_data.models import *
from django.conf import settings
import discord
from discord import Webhook, RequestsWebhookAdapter


from .models import *
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
    if request.META.get('HTTP_AUTHORIZATION') == settings.AUTH_PASS:
        return render(
            request, 
            'keep_alive.html',
            {
                'server_name': 'Keeping Alive The Bot',
                'docs':settings.DOCS,
                'website':settings.WEBSITE
            }
        )
    else:
        return redirect(reverse('Home'))

def invite_bot(request):
    return redirect(discord.utils.oauth_url(client_id=settings.DISCORD_CLIENT_ID, permissions=8))


def return_available_anime(request, name):
    name_id = AnimeName.objects.filter(anime_name__in=name).all()
    anime = [i.anime_name for i in AnimeName.objects.iterator()]

    #return JsonResponse(anime, safe=False)
