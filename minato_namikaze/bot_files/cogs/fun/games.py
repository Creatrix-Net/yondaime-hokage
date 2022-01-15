import asyncio
import random
import time
from asyncio import TimeoutError, sleep
from random import choice
from string import ascii_letters
from typing import Union

import async_cleverbot as ac
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

from ...lib import Embed, ErrorEmbed, Tokens, generatevoteembed, votedTopgg
from ...lib.classes.games import *


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.chatbot = ac.Cleverbot(Tokens.chatbot.value)
        self.description = "Play some amazing games"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{FLYING DISC}")

    @commands.command(aliases=["tc"], usage="<other player.mention>")
    @commands.guild_only()
    async def tictactoe(self, ctx, member: Union[int, discord.Member]):
        """Play Amazing Tictactoe Game"""
        member = get_user(member, ctx)
        if member == ctx.author or member.bot:
            await ctx.send(embed=ErrorEmbed(
                description="*You cannot play this game yourself or with a bot*"
            ))
            return
        await ctx.send(embed=Embed(
            description=f"*Positions are marked with 1,2,3.. just like 3x3 cube*\n{ctx.author.mention} you are taking *cross*\n{member.mention} you are taking *circle*"
        ))
        game = tictactoe.Tictactoe(
            cross=ctx.author,
            circle=member,
        )
        await game.start(ctx, remove_reaction_after=True)

    @commands.command(aliases=["connect_four", "c4", "cf"],
                      usage="<other player.mention>")
    @commands.guild_only()
    async def connectfour(self, ctx, member: Union[int, discord.Member]):
        """Play Amazing Connect Four Game"""
        member = get_user(member, ctx)
        if member == ctx.author or member.bot:
            await ctx.send(embed=ErrorEmbed(
                description="*You cannot play this game yourself or with a bot*"
            ))
            return
        await ctx.send(embed=Embed(
            description="**Here is the link to know about** *Connect Four*: [Click Here](<https://en.wikipedia.org/wiki/Connect_Four#firstHeading>)"
        ))
        await ctx.send(f"{ctx.author.mention} you are taking *red*")
        await ctx.send(f"{member.mention} you are taking *blue*")
        game = connect_four.ConnectFour(
            red=ctx.author,
            blue=member,
        )
        await game.start(ctx, remove_reaction_after=True)

    @commands.command(aliases=["hg"])
    async def hangman(self, ctx):
        """Play Hangman!"""
        await ctx.send(embed=Embed(
            description="**Here is the link to know about** *Hangman*: [Click Here](<https://en.wikipedia.org/wiki/Hangman_(game)#Example_game>)"
        ))

        await ctx.send(
            "__After execution__ of **hangman** command *reply* to the embed *to guess the word/movie.*"
        )
        game = hangman.Hangman()
        await game.start(ctx)

    @commands.command(aliases=["aki"])
    async def akinator(self, ctx):
        """Play Akinator"""
        await ctx.send(embed=Embed(
            description="**Here is the link to know about** *Akinator*: [Click Here](<https://en.wikipedia.org/wiki/Akinator#Gameplay>)"
        ))
        a = await ctx.send("**Now get ready for the game**")
        await asyncio.sleep(1)
        await a.edit(content="Starting in 5 seconds")
        for i in range(4):
            await a.edit(content=4 - i)
            await asyncio.sleep(1)
        await a.delete()
        game = aki.Akinator()
        await game.start(ctx)

    @commands.command()
    async def youtube(self, ctx):
        if check_if_user_joined_a_channel:
            link = await self.togetherControl.create_link(
                ctx.author.voice.channel.id, "youtube")
            await ctx.send(f"Click the blue link!\n{link}")
            return
        e = ErrorEmbed(
            title="No voice channel joined!",
            description="You need to join the voice channel in order to use this command :)",
        )
        await ctx.send(embed=e)

    @commands.command()
    async def poker(self, ctx):
        if check_if_user_joined_a_channel:
            link = await self.togetherControl.create_link(
                ctx.author.voice.channel.id, "poker")
            await ctx.send(f"Click the blue link!\n{link}")
        e = ErrorEmbed(
            title="No voice channel joined!",
            description="You need to join the voice channel in order to use this command :)",
        )
        await ctx.send(embed=e)

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.command(aliases=["cb"])
    async def chatbot(self, ctx):
        """Talk with me! (Vote Locked)"""
        async with ctx.typing():
            if not votedTopgg(ctx):
                await ctx.send(embed=generatevoteembed(ctx, "top.gg"))
                return
        lis = "cancel"
        transmit = True
        await ctx.send(
            f"Chatbot Started!\nType the following items `{lis}` to end.")
        while transmit is True:
            try:
                m = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda m:
                    (ctx.author == m.author and ctx.channel == m.channel),
                )
            except asyncio.TimeoutError:
                await ctx.send("I'm bored now, you should of been quicker...")
                transmit = False
            else:
                if m.content.lower() == lis:
                    transmit = False
                    left = await self.bot.chatbot.ask("bye")
                    await ctx.send(
                        f"{left.text}... Waiting... OH you said cancel, bye!")
                else:
                    async with ctx.channel.typing():
                        response = await self.bot.chatbot.ask(
                            m.content if len(m.content) >= 3 else
                            f"{m.content} {ascii_letters[choice(range(len(ascii_letters)))]}"
                        )
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
            description=f"So, {random.choice(lis)} fighter has challenged people to a game of....Cookie? Okay then get ready!"
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(4)
        for i in reversed(range(1, 4)):
            await message.edit(embed=discord.Embed(description=str(i)))
            await asyncio.sleep(1)
        await asyncio.sleep(random.randint(1, 3))
        await message.edit(embed=discord.Embed(
            description=f"React to the {reaction}!"))
        await message.add_reaction(reaction)
        start = time.perf_counter()
        try:
            _, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda _reaction, user: _reaction.message.guild == ctx.
                guild and _reaction.message.channel == ctx.message.channel and
                _reaction.message == message and str(_reaction.emoji) ==
                reaction and user != ctx.bot.user and not user.bot,
                timeout=60,
            )
        except asyncio.TimeoutError:
            return await message.edit(embed=discord.Embed(
                description="No one ate the cookie..."))
        end = time.perf_counter()
        await message.edit(embed=discord.Embed(
            description=f"**{user}**  ate the cookie in ```{end - start:.3f}``` seconds!"))
        lis3 = ["1", "2"]
        choice = random.choice(lis3)
        if choice == 2:
            await user.send(
                f"Firstly, Random chose 2 so you get this DM, Secondly, Well Done! You completed it in ```{end - start:.3f}``` seconds."
            )
        else:
            pass


def setup(bot):
    bot.add_cog(Games(bot))
