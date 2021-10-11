import datetime
import time

import discord


async def get_welcome_channel(guild: discord.Guild, bot: discord.Client, inviter_or_guild_owner: discord.User):
    try:
        return guild.system_channel
    except:
        try:
            text_channels_list = guild.text_channels
            for i in text_channels_list:
                if i.permissions_for(bot.user).send_messages:
                    return i
        except:
            return inviter_or_guild_owner

#R.Danny Code
class plural:
    def __init__(self, value):
        self.value = value
    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'

#R.Danny Code
def human_join(seq, delim=', ', final='or'):
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'

#R.Danny Code
def format_dt(dt, style=None):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    if style is None:
        return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'

