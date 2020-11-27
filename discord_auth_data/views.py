from __future__ import unicode_literals

import logging
from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import make_aware
from requests_oauthlib import OAuth2Session

from .conf import settings
from .models import DiscordInvite, DiscordUser

logger = logging.getLogger(__name__)


def oauth_session(request, state=None, token=None):
    """ Constructs the OAuth2 session object. """
    if settings.DISCORD_REDIRECT_URI is not None:
        redirect_uri = settings.DISCORD_REDIRECT_URI
    else:
        redirect_uri = request.build_absolute_uri(
            reverse('discord_bind_callback'))
    scope = ['identify', 'email','guilds','messages.read']
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


@login_required
def index(request):
    # Record the final redirect alternatives
    if 'invite_uri' in request.GET:
        request.session['discord_bind_invite_uri'] = request.GET['invite_uri']
    else:
        request.session['discord_bind_invite_uri'] = (
                settings.DISCORD_INVITE_URI)

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


@login_required
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
            data['expiry'] = expiry
        except KeyError:
            pass
        return data

    def bind_user(request, data):
        """ Create or update a DiscordUser instance """
        uid = data.pop('uid')
        count = DiscordUser.objects.filter(uid=uid).update(user=request.user,
                                                           **data)
        if count == 0:
            DiscordUser.objects.create(uid=uid,
                                       user=request.user,
                                       **data)

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
    bind_user(request, data)

    # Accept Discord invites
    groups = request.user.groups.all()
    invites = DiscordInvite.objects.filter(active=True).filter(
                                        Q(groups__in=groups) | Q(groups=None))
    count = 0
    for invite in invites:
        r = requests.post(settings.DISCORD_BASE_URI + '/invites/' + invite.code)
        if r.status_code == requests.codes.ok:
            count += 1
            logger.info(('accepted Discord '
                         'invite for %s/%s') % (invite.guild_name,
                                                invite.channel_name))
        else:
            logger.error(('failed to accept Discord '
                          'invite for %s/%s: %d %s') % (invite.guild_name,
                                                        invite.channel_name,
                                                        r.status_code,
                                                        r.reason))

    # Select return target
    if count > 0:
        messages.success(request, '%d Discord invite(s) accepted.' % count)
        url = request.session['discord_bind_invite_uri']
    else:
        url = request.session['discord_bind_return_uri']

    # Clean up
    del request.session['discord_bind_oauth_state']
    del request.session['discord_bind_invite_uri']
    del request.session['discord_bind_return_uri']

    return HttpResponseRedirect(url)
