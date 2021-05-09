import time
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