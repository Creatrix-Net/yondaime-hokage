from typing import Optional, Union

import discord


async def get_dm(user: Optional[Union[int, discord.Member]], ctx=None):
    if isinstance(user, int):
        user = ctx.bot.get_user(user)
    return user.dm_channel if user.dm_channel else await user.create_dm()


def get_user(user: Union[int, discord.Member], ctx=None):
    if isinstance(user, int):
        user = ctx.bot.get_user(user)
    return user


def get_roles(role: Union[int, discord.Role], ctx=None):
    if isinstance(role, int):
        role = discord.utils.get(ctx.guild.roles, id=role)
    return role

async def get_bot_inviter(guild: discord.Guild, bot: discord.Client):
    try:
        async for i in guild.audit_logs(limit=1):
            return i.user
    except:
        return guild.owner
