from __future__ import annotations

import discord
from discord.ext import commands

from minato_namikaze.lib import INVITE_URL_RE


class DmInvite(commands.Cog):
    """Respond to invites send in DMs."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    async def dminvite(self, ctx):
        """Group Commands for DM Invites."""

    @dminvite.command()
    @commands.is_owner()
    async def settings(self, ctx):
        """DM Invite Settings."""
        embed = discord.Embed(title="DM Invite Settings", color=discord.Color.red())
        embed.add_field(
            name="Tracking Invites",
            value="Yes" if await self.config.toggle() else "No",
        )
        embed.add_field(
            name="Embeds", value="Yes" if await self.config.embed() else "No"
        )
        msg = await self.config.message()
        embed.add_field(name="Message", value=msg)
        embed.add_field(
            name="Permissions Value", value=await self.bot._config.invite_perm()
        )
        if "{link}" in msg:
            embed.add_field(
                name="Link",
                value=f"[Click Here]({self.bot.get_required_perms_invite_link})",
            )
        await ctx.send(embed=embed)

    @dminvite.command()
    @commands.is_owner()
    async def toggle(self, ctx, toggle: bool = None):
        """Turn DM responding on/off."""
        toggle = toggle or await self.config.toggle()
        if toggle:
            await self.config.toggle.set(False)
            await ctx.send(
                f"{ctx.me.name} will no longer auto-respond to invites sent in DMs."
            )

        else:
            await self.config.toggle.set(True)
            await ctx.send(f"{ctx.me.name} will auto-respond to invites sent in DMs.")

    @dminvite.command()
    @commands.is_owner()
    async def embeds(self, ctx, toggle: bool = None):
        """Toggle whether the message is an embed or not."""
        toggle = toggle or await self.config.embed()
        if toggle:
            await self.config.embed.set(False)
            await ctx.send("Responses will no longer be sent as an embed.")
        else:
            await self.config.embed.set(True)
            await ctx.send(
                "Responses will now be sent as an embed. You can now use other markdown such as link masking etc.",
            )

    @dminvite.command()
    @commands.is_owner()
    async def message(self, ctx, *, message: str):
        """Set the message that the bot will respond with.

        **Available Parameters**:
        {link} - return the bots oauth url with the permissions you've set with the core inviteset.
        """
        await self.config.message.set(message)
        await ctx.tick()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            return
        if message.author.bot:
            return
        if link_res := INVITE_URL_RE.findall(message.content):
            msg = await self.config.message()
            if "{link}" in msg:
                msg = msg.format(link=await self.bot.get_required_perms_invite_link)
            if await self.config.embed():
                embed = discord.Embed(color=discord.Color.red(), description=msg)
                await message.author.send(embed=embed)
                return
            await message.author.send(msg)
