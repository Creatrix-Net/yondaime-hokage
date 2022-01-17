import discord
from discord.ext import menus
from discord.ext.menus.views import ViewMenu

from ...util import SetupVars
from ..embed import Embed


class Warns(ViewMenu):
    def __init__(self, bot, timeout, channel):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.channel = channel

    async def send_initial_message(self, ctx, channel):
        embed = Embed(
            title=f"Want a warning system for the **{ctx.guild.name}** ?")
        embed.add_field(name="Yes", value=":white_check_mark:")
        embed.add_field(name="No", value=":negative_squared_cross_mark:")
        return await channel.send(embed=embed)

    @menus.button("\N{WHITE HEAVY CHECK MARK}")
    async def on_add(self, payload):
        bingo = (discord.utils.get(
            self.ctx.guild.categories, name="Bingo Book") if discord.utils.get(
                self.ctx.guild.categories, name="Bingo Book") else False)
        if not bingo:
            bingo = await self.ctx.guild.create_category(
                "Bingo Book",
                reason="To log the the bans and unban events + warns")
        unban = await self.ctx.guild.create_text_channel(
            "warns",
            topic=SetupVars.warns.value,
            overwrites={
                self.ctx.guild.default_role:
                discord.PermissionOverwrite(read_messages=False,
                                            send_messages=False)
            },
            category=discord.utils.get(self.ctx.guild.categories,
                                       name="Bingo Book"),
        )

        await self.channel.send(
            f"{unban.mention} channel **created** for logging the **warns** for the {self.ctx.guild.name}"
        )
        e = Embed(
            description="This channel will be used to log the server members warn.")
        a = await unban.send(embed=e)
        await a.pin()
        return

    @menus.button("\N{NEGATIVE SQUARED CROSS MARK}")
    async def on_stop(self, payload):
        await self.channel.send(
            f"**Okay** no warning system for the **{self.ctx.guild.name}** warns will be there"
        )
        return
