from __future__ import annotations

import discord
from discord.ext import commands

from minato_namikaze.lib.database.config_api import Config

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config("Core", identifier="core")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def cog(self, ctx: commands.Context):
        """Manage bot features in this server."""
        await ctx.send_help(ctx.command)

    @cog.command()
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx: commands.Context, cog_name: str):
        """Disable a cog in this server."""
        if not self.bot.get_cog(cog_name):
            return await ctx.send("Cog not found. Please provide a valid loaded cog name (case-sensitive).")
        if cog_name == "Core":
            return await ctx.send("You cannot disable the Core configuration cog.")
        
        disabled = await self.config.guild(ctx.guild).get_attr("disabled_cogs", [])
        if cog_name not in disabled:
            disabled.append(cog_name)
            await self.config.guild(ctx.guild).set_attr("disabled_cogs", disabled)
        await ctx.send(f"{cog_name} has been disabled in this server.")

    @cog.command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx: commands.Context, cog_name: str):
        """Enable a previously disabled cog in this server."""
        disabled = await self.config.guild(ctx.guild).get_attr("disabled_cogs", [])
        if cog_name in disabled:
            disabled.remove(cog_name)
            await self.config.guild(ctx.guild).set_attr("disabled_cogs", disabled)
        await ctx.send(f"{cog_name} has been enabled in this server.")

async def setup(bot):
    await bot.add_cog(Core(bot))
