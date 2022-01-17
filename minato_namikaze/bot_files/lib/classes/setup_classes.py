import discord
from discord.ext import menus

from ..util import SetupVars
from .embed import Embed

ban_topic = SetupVars.ban.value
feedback_topic = SetupVars.feedback.value
support_topic = SetupVars.support.value
unban_topic = SetupVars.unban.value
warns_topic = SetupVars.warns.value


async def check():
    pass


class Ban:
    def __init__(self, ctx, timeout: int, channel: discord.TextChannel):
        self.ctx = ctx
        self.channel = channel
        self.timeout = timeout

    async def start(self):
        if not await self.ctx.prompt(
                f"Want to **log bans** for the *{self.ctx.guild.name}* ?",
                timeout=self.timeout,
                author_id=ctx.author.id,
                channel=self.channel,
        ):
            return
        bingo = (discord.utils.get(
            self.ctx.guild.categories, name="Bingo Book") if discord.utils.get(
                self.ctx.guild.categories, name="Bingo Book") else False)
        if not bingo:
            bingo = await self.ctx.guild.create_category(
                "Bingo Book",
                reason="To log the the bans and unban events + warns")
        ban_channel = await self.ctx.guild.create_text_channel(
            "ban",
            topic=ban_topic,
            overwrites={
                self.ctx.guild.default_role:
                discord.PermissionOverwrite(read_messages=False,
                                            send_messages=False)
            },
            category=discord.utils.get(self.ctx.guild.categories,
                                       name="Bingo Book"),
        )

        await self.channel.send(
            f"{ban_channel.mention} channel **created** for logging the **ban** of the {self.ctx.guild.name} server."
        )
        e = Embed(
            description="This channel will be used to log the server bans.")
        a = await ban_channel.send(embed=e)
        await a.pin()
        return
