import discord
import asyncio
from ..classes import ErrorEmbed

def check_if_warning_system_setup(ctx):
    if discord.utils.get(ctx.guild.text_channels, topic='Warning of the server members will be logged here.'):
        return True
    else:
        False


def return_warning_channel(ctx):
    return discord.utils.get(ctx.guild.text_channels, topic='Warning of the server members will be logged here.')
