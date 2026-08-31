from __future__ import annotations

import asyncio
import datetime
import operator
import random

import discord
from minato_namikaze.lib.database.bank import bank
from discord.ext import commands
from minato_namikaze.lib.database.config_api import Config



class Cashdrop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config("Fun", "cashdrop")
        self.cache = {}
        asyncio.create_task(self.init_loop())

    def random_calc(self):
        ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            #'/':operator.truediv
        }
        num1 = random.randint(0, 12)
        num2 = random.randint(1, 10)
        op = random.choice(list(ops.keys()))
        answer = ops.get(op)(num1, num2)
        return f"What is {num1} {op} {num2}?\n", answer

    async def init_loop(self):
        await self.bot.wait_until_ready()
        await self.generate_cache()
        # while True:
        #     await asyncio.sleep(60)
        # await self.save()

    def cog_unload(self):
        self.bg_config_loop.cancel()
        asyncio.create_task(self.save_triggers())

    async def generate_cache(self):
        pass # Cache is bypassed, we fetch directly if active

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
            
        active = await self.config.guild(message.guild).get_attr("active", False)
        if not active:
            return
            
        chance = await self.config.guild(message.guild).get_attr("chance", 1)
        if random.randint(0, 100) > chance:
            return
            
        interval = await self.config.guild(message.guild).get_attr("interval", 60)
        
        # In-memory timestamps to avoid DB spam
        if message.guild.id not in self.cache:
            self.cache[message.guild.id] = {}
            
        last_time = self.cache[message.guild.id].get("timestamp")
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        
        if last_time and (now - last_time).total_seconds() < interval:
            return
            
        self.cache[message.guild.id]["timestamp"] = now
        
        channel_id = await self.config.guild(message.guild).get_attr("channel", None)
        channel = message.guild.get_channel(channel_id) if channel_id else message.channel
        if not channel:
            channel = message.channel
            
        maths = await self.config.guild(message.guild).get_attr("maths", True)
        cmin = await self.config.guild(message.guild).get_attr("credits_min", 50)
        cmax = await self.config.guild(message.guild).get_attr("credits_max", 550)
        
        if maths:
            string, answer = self.random_calc()
            msg = await channel.send(string)
            
            def check(m):
                return m.channel == channel and m.content == str(answer)
                
            try:
                answer_msg = await self.bot.wait_for("message", check=check, timeout=10)
            except asyncio.TimeoutError:
                await msg.edit(content="Too slow!")
                return
                
            creds = random.randint(cmin, cmax)
            await msg.edit(content=f"Correct! {answer_msg.author.mention} got {creds} {await bank.get_currency_name(guild=message.guild)}!")
            await bank.deposit_credits(answer_msg.author, creds)
        else:
            msg = await channel.send(f"Some {await bank.get_currency_name(guild=message.guild)} have fallen, type pickup to pick them up!")
            
            def check(m):
                return m.channel == channel and m.content == "pickup"
                
            try:
                pickup_msg = await self.bot.wait_for("message", check=check, timeout=10)
            except asyncio.TimeoutError:
                await msg.edit(content="Too slow!")
                return

            creds = random.randint(cmin, cmax)
            await msg.edit(content=f"{pickup_msg.author.mention} picked up {creds} {await bank.get_currency_name(guild=message.guild)}!")
            await bank.deposit_credits(pickup_msg.author, creds)

    @commands.group(name="cashdrop", aliases=["cd"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _cashdrop(self, ctx):
        """
        Manage the cashdrop
        """

    @_cashdrop.command(name="toggle")
    async def _toggle(self, ctx):
        """
        Toggle the cashdrop
        """
        guild = ctx.guild
        active = await self.config.guild(guild).get_attr("active", False)
        if active:
            await self.config.guild(guild).set_attr("active", False)
            await ctx.send("Cashdrop is now disabled")
        else:
            await self.config.guild(guild).set_attr("active", True)
            await ctx.send("Cashdrop is now enabled")
        await self.generate_cache()

    @_cashdrop.command(name="chance")
    async def _chance(self, ctx, chance: int):
        """
        Set the chance percent of the cashdrop
        """
        if chance < 0 or chance > 100:
            await ctx.send("Chance must be between 0 and 100")
            return
        guild = ctx.guild
        await self.config.guild(guild).set_attr("chance", chance)
        await ctx.send(f"Chance set to {chance}%")
        await self.generate_cache()

    @_cashdrop.command(name="interval")
    async def _interval(self, ctx, interval: int):
        """
        Set the interval in seconds between cashdrops
        """
        if interval < 0:
            await ctx.send("Interval must be greater than 0")
            return
        guild = ctx.guild
        await self.config.guild(guild).set_attr("interval", interval)
        await ctx.send(f"Interval set to {interval} seconds")
        await self.generate_cache()

    @_cashdrop.command(name="max")
    async def _max(self, ctx, max: int):
        """
        Set the max credits
        """

        if max < 0:
            await ctx.send("Max must be greater than 0")
            return
        mincredits = await self.config.guild(ctx.guild).get_attr("credits_min", 50)
        if max < mincredits:
            await ctx.send("Max must be greater than min")
            return
        guild = ctx.guild
        await self.config.guild(guild).credits_max.set(max)
        await ctx.send(f"Max credits set to {max}")
        await self.generate_cache()

    @_cashdrop.command(name="min")
    async def _min(self, ctx, min: int):
        """
        Set the min credits
        """

        if min < 0:
            await ctx.send("Min must be greater than 0")
            return
        maxcredits = await self.config.guild(ctx.guild).get_attr("credits_max", 550)
        if maxcredits < min:
            await ctx.send("Min must be less than min")
            return
        guild = ctx.guild
        await self.config.guild(guild).credits_min.set(min)
        await ctx.send(f"Min credits set to {min}")
        await self.generate_cache()

    @_cashdrop.command(name="maths")
    async def _maths(self, ctx, toggle: bool):
        """
        Toggle maths mode
        """
        guild = ctx.guild
        if toggle:
            await self.config.guild(guild).set_attr("maths", True)
            await ctx.send("Maths mode is now enabled")
        else:
            await self.config.guild(guild).set_attr("maths", False)
            await ctx.send("Maths mode is now disabled")
        await self.generate_cache()

    @_cashdrop.command(name="channel")
    async def _channel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel for the cashdrop
        """
        guild = ctx.guild
        await self.config.guild(guild).channel.set(channel.id)
        await ctx.send(f"Channel set to {channel.mention}")
        await self.generate_cache()

async def setup(bot):
    await bot.add_cog(Cashdrop(bot))
