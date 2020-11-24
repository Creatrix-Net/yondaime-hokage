from __future__ import unicode_literals

from django.conf import settings
from appconf import AppConf


class DiscordBindConf(AppConf):
    """ Application settings """
    # API service endpoints
    BASE_URI = 'https://discordapp.com/api'
    AUTHZ_PATH = '/oauth2/authorize'
    TOKEN_PATH = '/oauth2/token'

    # OAuth2 application credentials
    CLIENT_ID = None
    CLIENT_SECRET = None

    # OAuth2 scope
    EMAIL_SCOPE = True

    # URI settings
    REDIRECT_URI = None
    INVITE_URI = 'https://discordapp.com/channels/@me'
    RETURN_URI = '/'

    class Meta:
        proxy = True
        prefix = 'discord'
        required = ['CLIENT_ID', 'CLIENT_SECRET']
