from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from DiscordUtils import Embed
from lib import serverinfo, userinfo

if TYPE_CHECKING:
    from lib import Context

    from ... import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)

class Info(commands.Cog):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github
        self.description = "Get's the Information about the server"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{INFORMATION SOURCE}")

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx: "Context", *, user: discord.Member = None):
        """Get the avatar of you or someone else"""
        user = user or ctx.author
        e = discord.Embed(title=f"Avatar for {user.name}")
        e.set_image(url=user.avatar.url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx: "Context", *, user: discord.Member = None):
        """Check when a user joined the current server"""
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=f"**{user}**",
            description=f"{user} joined **{ctx.guild.name}** at \n{user.joined_at}",
        )
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.group(aliases=["serverinfo"])
    @commands.guild_only()
    async def server(self, ctx: "Context"):
        """Check info about current server"""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=await serverinfo(ctx.guild, ctx.author, self.bot))

    @server.command(name="server_icon", aliases=["icon"])
    @commands.guild_only()
    async def server_icon(self, ctx: "Context"):
        """Get the current server icon"""
        if not ctx.guild.icon:
            return await ctx.send("This server does not have a avatar...")
        await ctx.send(
            f"Avatar of **{ctx.guild.name}**\n{ctx.guild.icon.with_size(1024).url}"
        )

    @server.command(name="banner")
    @commands.guild_only()
    async def server_banner(self, ctx: "Context"):
        """Get the current banner image"""
        if not ctx.guild.banner:
            return await ctx.send("This server does not have a banner...")
        e = Embed(title=f":information_source: Banner for {ctx.guild}")
        e.set_image(url=ctx.guild.banner.with_format("png").url)
        await ctx.send(embed=e)

    @commands.command(aliases=["whois", "who", "userinfo"])
    @commands.guild_only()
    async def user(self, ctx: "Context", *, user: discord.Member = None):
        """Get user information"""
        user = user or ctx.author
        await ctx.send(embed=await userinfo(user, ctx.guild, self.bot))


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Info(bot))
