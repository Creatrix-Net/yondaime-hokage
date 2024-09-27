from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from minato_namikaze.lib.functions.moderation import is_admin
from minato_namikaze.lib.util import owners
from minato_namikaze.lib.util.chat_formatting import humanize_list
from minato_namikaze.lib.util.utility import UniqueList
from minato_namikaze.lib.util.vars import ChannelAndMessageId

if TYPE_CHECKING:
    from ... import MinatoNamikazeBot


class Forward(commands.Cog):
    """Forward messages sent to the bot to the bot owner or in a specified channel. [developer only]"""

    def __init__(self, bot):
        self.bot = bot
        self.blacklist: UniqueList = UniqueList()

    async def _destination(self, msg: str = None, embed: discord.Embed = None):
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(
            ChannelAndMessageId.forward_dm_messages_channel_id.value
        )
        if channel is None:
            await self.bot.send_to_owners(msg, embed=embed)
        else:
            await channel.send(msg, embed=embed)

    @staticmethod
    def _append_attachements(message: discord.Message, embeds: list):
        attachments_urls = []
        for attachment in message.attachments:
            if any(
                attachment.filename.endswith(imageext)
                for imageext in ["jpg", "png", "gif"]
            ):
                if embeds[0].image:
                    embed = discord.Embed()
                    embed.set_image(url=attachment.url)
                    embeds.append(embed)
                else:
                    embeds[0].set_image(url=attachment.url)
            else:
                attachments_urls.append(f"[{attachment.filename}]({attachment.url})")
        if attachments_urls:
            embeds[0].add_field(name="Attachments", value="\n".join(attachments_urls))
        return embeds

    @commands.Cog.listener()
    async def on_message_without_command(self, message):
        if message.guild is not None:
            return
        recipient = message.channel.recipient
        if recipient is None:
            chan = self.bot.get_channel(message.channel.id)
            if chan is None:
                chan = await self.bot.fetch_channel(message.channel.id)
            if not isinstance(chan, discord.DMChannel):
                return
            recipient = chan.recipient
        if recipient.id in self.bot.owner_ids:
            return
        msg = ""
        if message.author == self.bot.user:
            msg = f"Sent PM to {recipient} (`{recipient.id}`)"
            if message.embeds:
                msg += f"\n**Message Content**: {message.content}"
                embeds = [
                    discord.Embed.from_dict(
                        {
                            **message.embeds[0].to_dict(),
                            "timestamp": str(message.created_at),
                        },
                    ),
                ]
            else:
                embeds = [discord.Embed(description=message.content)]
                embeds[0].set_author(
                    name=f"{message.author} | {message.author.id}",
                    icon_url=message.author.display_avatar,
                )
                embeds = self._append_attachements(message, embeds)
                embeds[-1].timestamp = message.created_at
        else:
            embeds = [discord.Embed(description=message.content)]
            embeds[0].set_author(
                name=f"{message.author} | {message.author.id}",
                icon_url=message.author.display_avatar.url,
            )
            embeds = self._append_attachements(message, embeds)
            embeds[-1].timestamp = message.created_at
        for embed in embeds:
            await self._destination(msg=msg, embed=embed)

    @commands.check(owners)
    @commands.group()
    async def forwardset(self, ctx):
        """Forwarding commands."""

    @forwardset.command(aliases=["bl"])
    async def blacklist(self, ctx: commands.Context, user_id: int = None):
        """Blacklist receiving messages from a user."""
        if not user_id:
            e = discord.Embed(
                color=await ctx.embed_color(),
                title="Forward Blacklist",
                description=humanize_list(self.blacklist),
            )
            await ctx.send(embed=e)
        else:
            if user_id in self.blacklist:
                await ctx.send("This user is already blacklisted.")
                return
            self.blacklist.append(int(user_id))
            await ctx.tick()

    @forwardset.command(aliases=["unbl"])
    async def unblacklist(self, ctx: commands.Context, user_id: int):
        """Remove a user from the blacklist."""
        if user_id not in self.blacklist:
            await ctx.send("This user is not in the blacklist.")
            return
        index = self.blacklist.index(user_id)
        self.blacklist.pop(index)
        await ctx.tick()

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def pm(self, ctx, user: discord.Member, *, message: str):
        """PMs a person.

        Separate version of [p]dm but allows for guild owners. This only works for users in the
        guild.
        """
        em = discord.Embed(colour=discord.Colour.red(), description=message)

        if ctx.bot.user.display_avatar:
            em.set_author(
                name=f"Message from {ctx.author} | {ctx.author.id}",
                icon_url=ctx.bot.user.display_avatar,
            )
        else:
            em.set_author(name=f"Message from {ctx.author} | {ctx.author.id}")

        try:
            await user.send(embed=em)
        except discord.Forbidden:
            await ctx.send(
                "Oops. I couldn't deliver your message to {}. They most likely have me blocked or DMs closed!",
            )
        await ctx.send(f"Message delivered to {user}")


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Forward(bot))
