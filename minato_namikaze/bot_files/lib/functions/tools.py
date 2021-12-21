import datetime
import time
import pytz
from typing import Optional, Union, Literal

import discord


def check_if_user_joined_a_channel(ctx):
    try:
        voice_state_author = ctx.author.voice
        if voice_state_author is None:
            return False
        return True
    except:
        return False


async def get_welcome_channel(guild: discord.Guild, bot: discord.Client,
                              inviter_or_guild_owner: discord.User):
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


# R.Danny Code
class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


# R.Danny Code
def human_join(seq, delim=", ", final="or"):
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


# R.Danny Code
def format_dt(dt, style: Optional[str] = None, ist: Optional[Union[bool, Literal[False]]] = False):
    if dt.tzinfo is None and not ist:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    if ist:
        timezone = datetime.timezone(datetime.timedelta(hours=5,minutes=30))  
        dt = dt.replace(tzinfo=timezone)  

    if style is None:
        return f"<t:{int(dt.timestamp())}>"
    return f"<t:{int(dt.timestamp())}:{style}>"
