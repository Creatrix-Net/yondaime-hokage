import gzip
from os.path import join
from pathlib import Path
from random import choice

import aiohttp

from DiscordUtils.embeds import Embed, ErrorEmbed

with gzip.open(
        join(
            Path(__file__).resolve().parent.parent,
            "data",
            "vocaloid_images.txt.gz",
        ),
        "rt",
        encoding="utf-8",
) as f:
    imageslist: list = f.readlines()


async def meek_api(name: str):
    session = aiohttp.ClientSession()

    l = (choice(["https://api.meek.moe/", False])
         if name.lower() == "miku" else "https://api.meek.moe/")
    e = Embed(title=name.capitalize())
    try:
        if name == "miku" and l:
            data = await session.get(l + name if l == "https://api.meek.moe/"
                                     else "https://api.meek.moe/")
            url = await data.json()
        else:
            data = await session.get(l + name)
            url = await data.json()
        e.set_image(url=url["url"])
    except:
        if name == "miku":
            e.set_image(url=choice(imageslist))
        else:
            e = ErrorEmbed(title="Sorry but currently there is some problem!")
            e.set_image(url=choice(imageslist))
    await session.close()
    return e
