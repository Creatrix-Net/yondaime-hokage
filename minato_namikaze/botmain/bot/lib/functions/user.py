import discord
from typing import Optional, Union

async def get_dm(user: Optional[Union[int, discord.Member]]):
    if isinstance(user, int):
        user = discord.get_user(user)
    
    return user.dm_channel if user.dm_channel else await user.create_dm()

def get_user(user: Optional[Union[int, discord.Member]]):
    if isinstance(user, int):
        user = discord.get_user(user)
    return user
    