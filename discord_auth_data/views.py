from __future__ import unicode_literals

from datetime import datetime

import requests
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import make_aware
from requests_oauthlib import OAuth2Session

from django.conf import settings

def logout(request):
    try:
        del request.session[str(request.session.session_key)]
    except: pass
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def oauth_session(request, state=None, token=None):
    """ Constructs the OAuth2 session object. """
    if settings.DISCORD_REDIRECT_URI is not None:
        redirect_uri = settings.DISCORD_REDIRECT_URI
    else:
        redirect_uri = request.build_absolute_uri(reverse('discord_bind_callback'))
    
    scope = ['identify', 'email',]
    return OAuth2Session(client_id=settings.DISCORD_CLIENT_ID,
                         redirect_uri=redirect_uri,
                         auto_refresh_kwargs={
                            'client_id': settings.DISCORD_CLIENT_ID,
                            'client_secret': settings.DISCORD_CLIENT_SECRET,
                        },
                         scope=scope,
                         token=token,
                         state=state
                         )

def index(request):
    # Record the final redirect alternatives
    if 'return_uri' in request.GET:
        request.session['discord_bind_return_uri'] = request.GET['return_uri']
    else:
        request.session['discord_bind_return_uri'] = (
                settings.DISCORD_RETURN_URI)

    # Compute the authorization URI
    oauth = oauth_session(request)
    url, state = oauth.authorization_url(settings.DISCORD_BASE_URI +
                                         settings.DISCORD_AUTHZ_PATH)
    request.session['discord_bind_oauth_state'] = state
    return HttpResponseRedirect(url)


def callback(request):
    def decompose_data(user, token):
        """ Extract the important details """
        data = {
            'uid': user['id'],
            'username': user['username'],
            'discriminator': user['discriminator'],
            'email': user.get('email', ''),
            'avatar': user.get('avatar', ''),
            'access_token': token['access_token'],
            'refresh_token': token.get('refresh_token', ''),
            'scope': ' '.join(token.get('scope', '')),
        }
        for k in data:
            if data[k] is None:
                data[k] = ''
        try:
            expiry = datetime.fromtimestamp(float(token['expires_in']))
            if settings.USE_TZ:
                expiry = make_aware(expiry)
            data['expiry'] = datetimeconverter(expiry)
        except KeyError:
            pass
        return data
    
    def datetimeconverter(o):
        if isinstance(o, datetime):
            return o.__str__()

    async def bind_user(request, data):
        """ Create or update a DiscordUser instance """
        from .bot_ipc_connect import BotIPCConnect
        a=BotIPCConnect()
        data.update({'guilds': await a.ipc_client.request("get_user_access_server", user=data['uid'])})
        request.session[str(request.session.session_key)] = data

    state = request.session['discord_bind_oauth_state'] 
    if 'state' not in request.GET or request.GET['state'] != state:
        return HttpResponseForbidden()
    data = {
        'client_id': settings.DISCORD_CLIENT_ID,
        'client_secret': settings.DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': request.GET.get('code'),
        'redirect_uri': request.build_absolute_uri(reverse('discord_bind_callback')),
        'scope': 'identify email connections guild',
        'state': request.GET.get('state'),
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(settings.DISCORD_BASE_URI+settings.DISCORD_TOKEN_PATH, data=data, headers=headers)
    response.raise_for_status()
    credentials = response.json()
    access_token = credentials.get('access_token')

    # Get Discord user data
    users = requests.get(f'{settings.DISCORD_BASE_URI }/users/@me', 
    headers={
        'Authorization': f'{credentials.get("token_type")} {access_token}',
    })
    data = decompose_data(users.json(), credentials)
    import asyncio
    asyncio.run(bind_user(request, data))

    url = request.session['discord_bind_return_uri']

    # Clean up
    del request.session['discord_bind_oauth_state']
    del request.session['discord_bind_return_uri']

    return HttpResponseRedirect(url)
