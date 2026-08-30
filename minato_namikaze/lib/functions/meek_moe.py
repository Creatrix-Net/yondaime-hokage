from __future__ import annotations

import aiohttp
from minato_namikaze.lib.util.embeds import Embed, ErrorEmbed

async def meek_api(name: str):
    e = Embed(title=name.capitalize())
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.meek.moe/{name}") as data:
                if data.status == 200:
                    url = await data.json()
                    e.set_image(url=url["url"])
                else:
                    e = ErrorEmbed(title="Sorry, unable to fetch image right now!")
    except Exception:
        e = ErrorEmbed(title="Sorry, unable to fetch image right now!")
    return e
