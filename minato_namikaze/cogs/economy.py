from __future__ import annotations

import logging
import random
import time

import discord
from discord.ext import commands

from minato_namikaze.lib import has_permissions
from minato_namikaze.lib.database.bank import bank
from minato_namikaze.lib.database.bank import InsufficientFunds
from minato_namikaze.lib.database.config_api import Config

log = logging.getLogger(__name__)


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Economy and currency commands"
        self.daily_config = Config("Economy", "daily")

    @commands.command(aliases=["bal"])
    async def balance(self, ctx, user: discord.Member = None):
        """Check your or another user's balance."""
        user = user or ctx.author
        bal = await bank.get_balance(user)
        currency = await bank.get_currency_name(ctx.guild)

        embed = discord.Embed(
            title=f"{user.display_name}'s Balance",
            description=f"**{bal}** {currency}",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def pay(self, ctx, user: discord.Member, amount: int):
        """Transfer credits to another user."""
        if amount <= 0:
            return await ctx.send("You must transfer a positive amount.")
        if user == ctx.author:
            return await ctx.send("You cannot pay yourself.")

        currency = await bank.get_currency_name(ctx.guild)

        try:
            await bank.transfer_credits(ctx.author, user, amount)
            await ctx.send(
                f"Successfully transferred **{amount}** {currency} to {user.display_name}.",
            )
        except InsufficientFunds:
            await ctx.send(f"You don't have enough {currency} to do that.")

    @commands.command()
    async def daily(self, ctx):
        """Claim your daily credits."""
        user_conf = self.daily_config.user(ctx.author)
        last_claimed = await user_conf.get_attr("last_claimed", 0)

        now = int(time.time())
        cooldown = 86400  # 24 hours

        if now - last_claimed < cooldown:
            remaining = cooldown - (now - last_claimed)
            hours, remainder = divmod(remaining, 3600)
            minutes, _ = divmod(remainder, 60)
            return await ctx.send(
                f"You already claimed your daily! Try again in {hours}h {minutes}m.",
            )

        amount = 500
        await bank.deposit_credits(ctx.author, amount)
        await user_conf.set_attr("last_claimed", now)

        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(f"You claimed your daily **{amount}** {currency}!")

    @commands.command()
    async def gamble(self, ctx, amount: int):
        """Gamble your credits. 50% chance to double, 50% chance to lose it all."""
        if amount <= 0:
            return await ctx.send("You must gamble a positive amount.")

        currency = await bank.get_currency_name(ctx.guild)

        try:
            await bank.withdraw_credits(ctx.author, amount)
        except InsufficientFunds:
            return await ctx.send(
                f"You don't have enough {currency} to gamble that much.",
            )

        if random.choice([True, False]):
            winnings = amount * 2
            await bank.deposit_credits(ctx.author, winnings)
            await ctx.send(f"🎲 You won! You receive **{winnings}** {currency}!")
        else:
            await ctx.send(
                f"🎲 You lost **{amount}** {currency}. Better luck next time!",
            )

    @commands.command(aliases=["top"])
    async def leaderboard(self, ctx):
        """Show the wealthiest users."""
        top_users = await bank.get_leaderboard(guild=ctx.guild, limit=10)
        currency = await bank.get_currency_name(ctx.guild)

        if not top_users:
            return await ctx.send("The leaderboard is empty.")

        desc = ""
        for idx, (user_id, bal) in enumerate(top_users, start=1):
            desc += f"**{idx}.** <@{user_id}>: {bal} {currency}\n"

        embed = discord.Embed(
            title="Economy Leaderboard",
            description=desc,
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    @has_permissions(administrator=True)
    async def bankset(self, ctx):
        """Bank administration commands."""
        await ctx.send_help(ctx.command)

    @bankset.command(name="global")
    @has_permissions(administrator=True)
    async def set_global(self, ctx, is_global: bool):
        """Set whether the bank is global across all servers or local to each server."""
        conf = Config("Economy", "bank")
        await conf.global_().set_attr("is_global", is_global)
        state = "global" if is_global else "local to each server"
        await ctx.send(f"The bank is now set to **{state}**.")

    @bankset.command(name="name")
    @has_permissions(administrator=True)
    async def set_name(self, ctx, *, name: str):
        """Set the currency name. If bank is local, sets for this server."""
        conf = Config("Economy", "bank")
        is_glob = await bank.is_global()

        if is_glob:
            await conf.global_().set_attr("currency_name", name)
            await ctx.send(f"Global currency name set to **{name}**.")
        else:
            await conf.guild(ctx.guild).set_attr("currency_name", name)
            await ctx.send(f"Currency name for this server set to **{name}**.")

    @bankset.command(name="setbal")
    @has_permissions(administrator=True)
    async def set_balance(self, ctx, user: discord.Member, amount: int):
        """Set a user's exact balance."""
        if amount < 0:
            return await ctx.send("Balance cannot be negative.")

        await bank.set_balance(user, amount)
        currency = await bank.get_currency_name(ctx.guild)
        await ctx.send(f"Set {user.display_name}'s balance to **{amount}** {currency}.")


async def setup(bot):
    await bot.add_cog(Economy(bot))
