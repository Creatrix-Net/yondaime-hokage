import discord

from ..util import SetupVars
from .embed import Embed

bingo = "Bingo Book"
admin = "Admin / Feedback"
categories_dict = {
    "ban": bingo,
    "unban": bingo,
    "warns": bingo,
    "support": admin,
    "feedback": admin,
}

categories_dict_reason = {
    bingo: "To log the the bans and unban events + warns",
    admin: "Admin Only Category",
}


class SetupChannels:
    def __init__(self, ctx, timeout: int, channel: discord.TextChannel,
                 channel_type: SetupVars):
        self.ctx = ctx
        self.channel = channel
        self.timeout = timeout
        self.channel_type = channel_type

    async def start(self):
        if not await self.ctx.prompt(
                f"Want to **log {self.channel_type.name}** for the *{self.ctx.guild.name}* ?",
                timeout=self.timeout,
                author_id=self.ctx.author.id,
                channel=self.channel,
        ):
            return

        category_exists = (True if discord.utils.get(
            self.ctx.guild.categories,
            name=categories_dict.get(self.channel_type.name),
        ) else False)
        if not category_exists:
            category = await self.ctx.guild.create_category(
                "Bingo Book",
                reason="To log the the bans and unban events + warns")
        new_channel = await self.ctx.guild.create_text_channel(
            self.channel_type.name,
            topic=self.channel_type.value,
            overwrites={
                self.ctx.guild.default_role:
                discord.PermissionOverwrite(read_messages=False,
                                            send_messages=False)
            },
            category=category,
        )

        await self.channel.send(
            f"{new_channel.mention} channel **created** for logging the **{self.channel_type.name}** of the {self.ctx.guild.name} server."
        )
        e = Embed(
            description=f"This channel will be used to log the server {self.channel_type.name}."
        )
        a = await new_channel.send(embed=e)
        await a.pin()
        return
