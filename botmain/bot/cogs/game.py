# Discord Imports
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

# Time Imports
import datetime
import time

# Other Imports
import random
import asyncio

# Thanks Isirk for the cb command, I modified it, if your looking to take it please ask Isirk#0001 on discord


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.chatbot = bot.chatbot

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.command(aliases=['cb'])
    async def chatbot(self, ctx):
        '''Talk to chatbot'''
        lis = "cancel"
        transmit = True
        await ctx.send(f'Chatbot Started!\nType the following items `{lis}` to end.')
        while transmit is True:
            try:
                m = await self.bot.wait_for('message', timeout=30, check=lambda m: (ctx.author == m.author and ctx.channel == m.channel))
            except asyncio.TimeoutError:
                await ctx.send("I'm bored now, you should of been quicker...")
                transmit = False
            else:
                if m.content.lower() == lis:
                    transmit = False
                    left = await self.bot.chatbot.ask("bye")
                    await ctx.send(f"{left.text}... Waiting... OH you said cancel, bye!")
                else:
                    async with ctx.channel.typing():
                        response = await self.bot.chatbot.ask(m.content)
                        await ctx.send(response.text)

    @commands.max_concurrency(1, per=commands.BucketType.channel)
    @commands.command()
    async def reaction(self, ctx):
        """
        Yum Yum or Yuck Yuck?
        """
        cookies = ["🍪", "❤"]
        lis = ["this mighty", "this weak", "this amazing"]
        reaction = random.choices(cookies, weights=[0.9, 0.1], k=1)[0]
        embed = discord.Embed(
            description=f"So, {random.choice(lis)} fighter has challenged people to a game of....Cookie? Okay then get ready!")
        message = await ctx.send(embed=embed)
        await asyncio.sleep(4)
        for i in reversed(range(1, 4)):
            await message.edit(embed=discord.Embed(description=str(i)))
            await asyncio.sleep(1)
        await asyncio.sleep(random.randint(1, 3))
        await message.edit(embed=discord.Embed(description=f"React to the {reaction}!"))
        await message.add_reaction(reaction)
        start = time.perf_counter()
        try:
            _, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                and _reaction.message.channel == ctx.message.channel
                and _reaction.message == message and str(_reaction.emoji) == reaction and user != ctx.bot.user
                and not user.bot,
                timeout=60,)
        except asyncio.TimeoutError:
            return await message.edit(embed=discord.Embed(description="No one ate the cookie..."))
        end = time.perf_counter()
        await message.edit(embed=discord.Embed(description=f"**{user}**  ate the cookie in ```{end - start:.3f}``` seconds!"))
        lis3 = ["1", "2"]
        choice = random.choice(lis3)
        if choice == 2:
            await user.send(f"Firstly, Random chose 2 so you get this DM, Secondly, Well Done! You completed it in ```{end - start:.3f}``` seconds.")
        else:
            pass


def setup(bot):
    bot.add_cog(Games(bot))
