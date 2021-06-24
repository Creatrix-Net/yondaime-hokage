import time
import discord

async def create_paginator(bot, ctx, pages):
    msg = await ctx.send(embed=pages[0])

    for reaction in ["⏮️", "◀️", "⏹️", "▶️", "⏭️"]:
        await msg.add_reaction(reaction)

    await bot.state.sadd(
        "reaction_menus",
        {
            "kind": "paginator",
            "channel": msg.channel.id,
            "message": msg.id,
            "end": int(time.time()) + 180,
            "data": {
                "page": 0,
                "all_pages": [page.to_dict() for page in pages],
            },
        },
    )
    
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