from __future__ import annotations
import discord
from discord.ext import commands
from minato_namikaze.lib.database.config_api import Config
from minato_namikaze.lib import has_permissions

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config("Counting", "channels")

    @commands.group(invoke_without_command=True)
    async def counting(self, ctx):
        """Counting game commands."""
        await ctx.send_help(ctx.command)

    @counting.command(name="setup")
    @has_permissions(manage_channels=True)
    async def counting_setup(self, ctx, channel: discord.TextChannel):
        """Set up a counting game in a channel."""
        await self.config.guild(ctx.guild).set_attr("channel_id", channel.id)
        await self.config.guild(ctx.guild).set_attr("current_count", 0)
        await self.config.guild(ctx.guild).set_attr("last_user_id", None)
        await ctx.send(f"Counting channel set to {channel.mention}. Start with 1!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        guild_config = self.config.guild(message.guild)
        channel_id = await guild_config.get_attr("channel_id", None)

        if not channel_id or message.channel.id != channel_id:
            return

        try:
            number = int(message.content.strip())
        except ValueError:
            return # Ignore non-numbers

        current_count = await guild_config.get_attr("current_count", 0)
        last_user_id = await guild_config.get_attr("last_user_id", None)

        if number == current_count + 1:
            if message.author.id == last_user_id:
                await message.add_reaction("❌")
                await message.channel.send(f"{message.author.mention} ruined the count at **{current_count}** by counting twice in a row! Start over from 1.")
                await guild_config.set_attr("current_count", 0)
                await guild_config.set_attr("last_user_id", None)
            else:
                await message.add_reaction("✅")
                await guild_config.set_attr("current_count", number)
                await guild_config.set_attr("last_user_id", message.author.id)
        else:
            await message.add_reaction("❌")
            await message.channel.send(f"{message.author.mention} ruined the count at **{current_count}**. The next number was **{current_count + 1}**! Start over from 1.")
            await guild_config.set_attr("current_count", 0)
            await guild_config.set_attr("last_user_id", None)

async def setup(bot):
    await bot.add_cog(Counting(bot))
