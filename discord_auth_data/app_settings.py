from __future__ import unicode_literals

from django.conf import settings


# API service endpoints
BASE_URI = getattr(settings, 'DISCORD_BASE_URI',
                   'https://discordapp.com/api')
AUTHZ_URI = getattr(settings, 'DISCORD_AUTHZ_URI',
                    BASE_URI + '/oauth2/authorize')
TOKEN_URI = getattr(settings, 'DISCORD_TOKEN_URI',
                    BASE_URI + '/oauth2/token')

# OAuth2 application credentials
CLIENT_ID = getattr(settings, 'DISCORD_CLIENT_ID', '')
CLIENT_SECRET = getattr(settings, 'DISCORD_CLIENT_SECRET', '')

# OAuth2 scope
AUTHZ_SCOPE = (
    ['email', 'guilds.join'] if getattr(settings, 'DISCORD_EMAIL_SCOPE', True)
    else ['identity', 'guilds.join'])

# Return URI
INVITE_URI = getattr(settings, 'DISCORD_INVITE_URI',
                     'https://discordapp.com/channels/@me')
RETURN_URI = getattr(settings, 'DISCORD_RETURN_URI', '/')
