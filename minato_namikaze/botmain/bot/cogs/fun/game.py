import asyncio
import random
import time
from asyncio import TimeoutError, sleep
from random import choice

import async_cleverbot as ac
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord_components import Button, ButtonStyle, DiscordComponents

from ...lib import Embed, ErrorEmbed, chatbot


class FunGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.chatbot = ac.Cleverbot(f"{chatbot}")
        self.description = 'A simple reaction game and also here you can chat with me!'
        self.session_message = {}

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.command(aliases=['cb'])
    async def chatbot(self, ctx):
        '''Talk with me!'''
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

    @commands.command()
    async def cointoss(self, ctx):
        '''Toss a coin'''
        try:
            embed = Embed(
                title=f":coin: {ctx.author.name}'s coin toss :coin:",
                description="Pick heads or tails below!",
            )

            menu_components = [
                [
                    Button(style=ButtonStyle.grey, label="Heads"),
                    Button(style=ButtonStyle.grey, label="Tails"),
                ]
            ]
            heads_components = [
                [
                    Button(style=ButtonStyle.green,
                           label="Heads", disabled=True),
                    Button(style=ButtonStyle.red,
                           label="Tails", disabled=True),
                ],
                Button(style=ButtonStyle.blue,
                       label="Play Again?", disabled=False),
            ]
            tails_components = [
                [
                    Button(style=ButtonStyle.red,
                           label="Heads", disabled=True),
                    Button(style=ButtonStyle.green,
                           label="Tails", disabled=True),
                ],
                Button(style=ButtonStyle.blue,
                       label="Play Again?", disabled=False),
            ]

            if ctx.author.id in self.session_message:
                msg = self.session_message[ctx.author.id]
                await msg.edit(embed=embed, components=menu_components)
            else:
                msg = await ctx.send(embed=embed, components=menu_components)
                self.session_message[ctx.author.id] = msg

            def check(res):
                return res.user.id == ctx.author.id and res.channel.id == ctx.channel.id

            try:
                res = await self.bot.wait_for("button_click", check=check, timeout=20)
            except TimeoutError:
                await msg.edit(
                    embed=ErrorEmbed(
                        title="Timeout!", description="No-one reacted. :frowning2:"),
                    components=[
                        Button(style=ButtonStyle.red,
                               label="Oh-no! Timeout reached!", disabled=True)
                    ],
                )
                return

            await res.respond(
                type=7,
                embed=Embed(
                    title=f"🪙 {ctx.author.name}'s coin toss 🪙",
                    description=f"You chose **{res.component.label.lower()}**!",
                ),
                components=menu_components,
            )

            game_choice = choice(["Heads", "Tails"])
            await sleep(2)

            if game_choice == res.component.label:
                embed = Embed(
                    title=f"🪙 {ctx.author.name}'s coin toss 🪙",
                    description=f"You chose **{res.component.label.lower()}**!\n\n> **YOU WIN!**",
                )
            else:
                embed = ErrorEmbed(
                    title=f"🪙 {ctx.author.name}'s coin toss 🪙",
                    description=f"You chose **{res.component.label.lower()}**!\n\n> You lost.",
                )

            await msg.edit(
                embed=embed,
                components=tails_components if game_choice == "Tails" else heads_components,
            )

            try:
                res = await self.bot.wait_for("button_click", check=check, timeout=20)
            except TimeoutError:
                await msg.delete()
                del self.session_message[ctx.author.id]
                return

            await res.respond(type=6)
            if res.component.label == "Play Again?":
                self.session_message[ctx.author.id] = msg
                await self.cointoss(ctx)
        except:
            await ctx.send(embed=ErrorEmbed(description="Please run the command again!"))


def setup(bot):
    bot.add_cog(FunGames(bot))
