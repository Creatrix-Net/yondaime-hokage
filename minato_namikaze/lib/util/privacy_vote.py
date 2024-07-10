from __future__ import annotations

from asyncio import sleep as sl

import aiohttp
import discord
import orjson
from discord.ext import menus

from .embeds import Embed
from .embeds import ErrorEmbed
from .embeds import SuccessEmbed
from .vars import LinksAndVars


class VotingMenu(menus.Menu):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @staticmethod
    async def send_initial_message(ctx, channel):
        e = discord.Embed(
            title="I see you want vote!",
            description=f"{ctx.author.mention}, maybe react with your choice :)",
        )
        return await channel.send(embed=e)

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def on_check_mark(self, payload):
        async with aiohttp.ClientSession() as session, session.get(
            LinksAndVars.listing.value,
        ) as resp:
            listing: dict = orjson.loads(await resp.text())
        listing_formatted_string = "\n".join(
            f"- **[{i}](https://{listing[i]}/{self.bot.application_id})**"
            for i in listing
        )
        e1 = SuccessEmbed(
            title="Thanks!",
            description=f"Thanks {self.ctx.author.mention}! Here's the links:\n{listing_formatted_string}",
        )
        await self.message.edit(content="", embed=e1)
        self.stop()

    @menus.button("\N{NEGATIVE SQUARED CROSS MARK}")
    async def on_stop(self, payload):
        e2 = ErrorEmbed(
            title="Sorry to see you go!",
            description="Remember you can always re-run the command :)",
        )
        self.stop()
        await self.message.edit(content="", embed=e2)
        await sl(5)
        await self.message.delete()


class PrivacyPolicy(menus.Menu):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def send_initial_message(self, ctx, channel):
        e = discord.Embed(
            title="I see you want to know more!",
            description=f"{ctx.author.mention}, click the checkmark for the Privacy Policy or the crossmark for just info!",
        )
        return await channel.send(embed=e)

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def on_add(self, payload):
        e1 = SuccessEmbed(
            title="Well, Heres The Policy :)",
            description="Well well well, Nothing is stored! Really nothing is stored! All is based on internal cache provided by Discord! For more please visit [THIS LINK](https://dhruvacube.github.io/yondaime-hokage/privacy_policy)",
        )
        await self.message.edit(content="", embed=e1)

    @menus.button("\N{NEGATIVE SQUARED CROSS MARK}")
    async def on_stop(self, payload):
        e2 = Embed(
            title="Hey!",
            description=f"Hi, I'm {self.bot.user}, I am developed by {self.ctx.get_user(self.bot.owner_id)}, Who is a great fan of me i.e. {self.bot.user} aka Yondaime Hokage!",
        )

        await self.message.edit(content="", embed=e2)


class MenuSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, data):
        embed = discord.Embed(description="\n".join(item for item in data))
        return embed
