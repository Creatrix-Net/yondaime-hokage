import discord
from discord.ext import menus

from ..embed import Embed


class Feedback(menus.Menu):
    def __init__(self, bot):
        super().__init__(timeout=60.0)
        self.bot = bot

    async def send_initial_message(self, ctx, channel):
        embed = Embed(
            title=f"Want to create a feedback system for the **{ctx.guild.name}** ?")
        embed.add_field(name="Yes", value=":white_check_mark:")
        embed.add_field(name="No", value=":negative_squared_cross_mark:")
        return await channel.send(embed=embed)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_add(self, payload):
        feed = await self.ctx.guild.create_text_channel(
            "Feedback",
            topic='Feedback given by the members of the servers will be logged here.',
            category=discord.utils.get(
                self.ctx.guild.categories,
                name="Admin / Feedback")
        )
        await self.channel.send(f'{feed.mention} channel **created** for logging the **feedbacks** for the {self.ctx.guild.name} by members!')
        e = Embed(
            description='This channel will be used to log the feedbacks given by members.'
        )
        a = await feed.send(embed=e)
        await a.pin()
        return

    @menus.button('\N{NEGATIVE SQUARED CROSS MARK}')
    async def on_stop(self, payload):
        await self.channel.send(f'**Okay** no **feedback system** will be there for the **{self.ctx.guild.name}**')
        return