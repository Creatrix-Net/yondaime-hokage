import discord
from discord.ext import menus

from ..embed import Embed


class Unban(menus.Menu):
    def __init__(self, bot, timeout):
        super().__init__(timeout=timeout)
        self.bot = bot

    async def send_initial_message(self, ctx, channel):
        embed = Embed(
            title=f"Want to log unbans for the **{ctx.guild.name}** ?")
        embed.add_field(name="Yes", value=":white_check_mark:")
        embed.add_field(name="No", value=":negative_squared_cross_mark:")
        return await channel.send(embed=embed)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_add(self, payload):
        bingo = discord.utils.get(self.ctx.guild.categories, name="Bingo Book") if discord.utils.get(
            self.ctx.guild.categories, name="Bingo Book") else False
        if not bingo:
            bingo = await self.ctx.guild.create_category(
                "Bingo Book",
                reason="To log the the bans and unban events + warns"
            )
        unban = await self.ctx.guild.create_text_channel(
            "unban",
            topic='Unbans of the server will be logged here.',
            category=discord.utils.get(
                self.ctx.guild.categories,
                name="Bingo Book")
        )

        await self.channel.send(f'{unban.mention} channel **created** for logging the **unbans** for the {self.ctx.guild.name}')
        e = Embed(
            description='This channel will be used to log the server unban.'
        )
        a = await unban.send(embed=e)
        await a.pin()
        return

    @menus.button('\N{NEGATIVE SQUARED CROSS MARK}')
    async def on_stop(self, payload):
        await self.channel.send(f'**Okay** no logging system for the **{self.ctx.guild.name}** unbans will be there')
        return
