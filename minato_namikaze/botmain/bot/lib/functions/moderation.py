import discord
import asyncio
from ..classes import ErrorEmbed
from ..util import warns, support, ban, unban, feedback

#checks warns
def check_if_warning_system_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic=warns):
        return True
    else:
        return False

#checks support
def check_if_support_is_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic=support):
        support_channel = True
    else:
        support_channel = False
    return support_channel

#checks ban
def check_if_ban_channel_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic=ban):
        return True
    else:
        return False

#checks unban
def check_if_unban_channel_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic=unban):
        return True
    else:
        return False

#check feedback
def check_if_feedback_system_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic=feedback):
        return True
    else:
        return False

#return warns
def return_warning_channel(ctx = None, guild = None):
    return discord.utils.get(ctx.guild.text_channels if ctx else guild.text_channels, topic=warns)

def return_ban_channel(ctx = None, guild = None):
    return discord.utils.get(ctx.guild.text_channels if ctx else guild.text_channels, topic=ban)

def return_unban_channel(ctx = None, guild = None):
    return discord.utils.get(ctx.guild.text_channels if ctx else guild.text_channels, topic=unban)

def return_feedback_channel(ctx = None, guild = None):
    return discord.utils.get(ctx.guild.text_channels if ctx else guild.text_channels, topic=feedback)

def return_support_channel(ctx = None, guild = None):
    return discord.utils.get(ctx.guild.text_channels if ctx else guild.text_channels, topic=support)
