from os.path import join
from pathlib import Path
from random import choice
from ..classes.embed import Embed, ErrorEmbed

import aiohttp
import discord


async def meek_api(ctx, name):
    session = aiohttp.ClientSession()

    l = choice(['https://api.meek.moe/', 'https://mikuapi.predeactor.net/random',
               False]) if name.lower() == 'miku' else 'https://api.meek.moe/'
    e = Embed(title=name.capitalize())
    try:
        if name == 'miku' and l:
            data = await session.get(l + name if l == 'https://api.meek.moe/' else 'https://mikuapi.predeactor.net/random')
        else:
            data = await session.get(l + name)
            url = await data.json()
        e.set_image(url=url['url'])
    except:
        imageslistdir = Path(__file__).resolve(
            strict=True).parent.parent / join('text','vocaloid_images.txt')
        filepointer = open(imageslistdir)
        imageslist = filepointer.readlines()
        if name == 'miku':
            e.set_image(url=choice(imageslist))
        else:
            e = ErrorEmbed(
                title='Sorry but currently there is some problem!')
            e.set_image(url=choice(imageslist))
    await session.close()
    return e