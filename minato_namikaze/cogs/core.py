from __future__ import annotations
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


    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def perms(self, ctx: commands.Context):
        """Manage command permissions for this server."""
        await ctx.send_help(ctx.command)

    @perms.command(name="addrole")
    @commands.has_permissions(manage_guild=True)
    async def perms_addrole(self, ctx: commands.Context, command_name: str, role: discord.Role):
        """Allow a specific role to use a command."""
        cmd = self.bot.get_command(command_name)
        if not cmd:
            return await ctx.send("Command not found.")

        overrides = await self.config.guild(ctx.guild).get_attr("perm_overrides", {})
        cmd_overrides = overrides.setdefault(cmd.qualified_name, {"roles": [], "channels": [], "users": []})
        if role.id not in cmd_overrides["roles"]:
            cmd_overrides["roles"].append(role.id)
            await self.config.guild(ctx.guild).set_attr("perm_overrides", overrides)
        await ctx.send(f"Role {role.name} added to the allowlist for {cmd.qualified_name}.")

    @perms.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def perms_clear(self, ctx: commands.Context, command_name: str):
        """Clear all permission overrides for a command."""
        cmd = self.bot.get_command(command_name)
        if not cmd:
            return await ctx.send("Command not found.")

        overrides = await self.config.guild(ctx.guild).get_attr("perm_overrides", {})
        if cmd.qualified_name in overrides:
            del overrides[cmd.qualified_name]
            await self.config.guild(ctx.guild).set_attr("perm_overrides", overrides)
        await ctx.send(f"Cleared all custom permissions for {cmd.qualified_name}.")

async def setup(bot):
    await bot.add_cog(Core(bot))
