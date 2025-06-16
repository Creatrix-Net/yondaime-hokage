from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import discord
from discord.ext import commands

from minato_namikaze.lib import ErrorEmbed
from minato_namikaze.lib import MemberID
from minato_namikaze.lib.classes.games import *

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib import Context
    from ... import MinatoNamikazeBot


class Games(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Play some amazing games"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{FLYING DISC}")

    @commands.command(aliases=["tc"], usage="<other player.mention>")
    @commands.guild_only()
    async def tictactoe(
        self,
        ctx: "Context",
        member: MemberID | discord.Member | None = None,
    ):
        """
        Play Tictactoe with yourself or your friend!
        """
        member = member or ctx.me
        if member is ctx.author or member.bot and member is not ctx.me:
            await ctx.send(
                embed=ErrorEmbed(
                    description="*You cannot play this game yourself or with a bot*",
                ),
            )
            return
        view = TicTacToe(player2=member, player1=ctx.author, auto=member is ctx.me)
        view.message = await ctx.send(
            f"Tic Tac Toe: X goes first aka {ctx.author.mention}",
            view=view,
        )

    @commands.command(
        aliases=["connect_four", "c4", "cf"],
        usage="[other player.mention]",
    )
    @commands.guild_only()
    async def connectfour(
        self,
        ctx: "Context",
        member: MemberID | discord.Member | None = None,
    ):
        """
        Play Amazing Connect Four Game
        https://en.wikipedia.org/wiki/Connect_Four#firstHeading
        """
        member = member or ctx.me
        if member is ctx.author or member.bot and member is not ctx.me:
            await ctx.send(
                embed=ErrorEmbed(
                    description="*You cannot play this game yourself or with a bot*",
                ),
            )
            return
        view = ConnectFour(red=ctx.author, blue=member, auto=member is ctx.me)
        view.message = await ctx.send(
            embeds=[view.embed, view.BoardString()],
            view=view,
        )

    @commands.command(aliases=["hg"])
    async def hangman(self, ctx: "Context"):
        """: "Context"
        Play Hangman!
        https://en.wikipedia.org/wiki/Hangman_(game)#Example_game
        To play reply with a letter after the hangman embed
        """
        game = hangman.Hangman()
        await game.start(ctx)

    @commands.command(aliases=["aki"])
    async def akinator(self, ctx: "Context"):
        """
        Play Akinator
        https://en.wikipedia.org/wiki/Akinator#Gameplay
        """
        view = Akinator()
        await view.start()
        view.message = await ctx.send(embed=await view.build_embed(), view=view)

    @commands.command(aliases=["wpm", "typingspeed"])
    async def typeracer(self, ctx):
        """Check your typing speed via a simple typeracer test"""
        await TypeRacer().start(ctx=ctx)

    @commands.max_concurrency(1, per=commands.BucketType.channel)
    @commands.command()
    async def reaction(self, ctx: "Context"):
        """
        Yum Yum or Yuck Yuck?
        """
        cookies = ["\U0001f36a", "\U00002764"]
        lis = ["this mighty", "this weak", "this amazing"]
        reaction = random.choices(cookies, weights=[0.9, 0.1], k=1)[0]
        embed = discord.Embed(
            description=f"So, {random.choice(lis)} fighter has challenged people to a game of....Cookie? Okay then get ready!",
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(4)
        for i in reversed(range(1, 4)):
            await message.edit(embed=discord.Embed(description=str(i)))
            await asyncio.sleep(1)
        await asyncio.sleep(random.randint(1, 3))
        await message.edit(embed=discord.Embed(description=f"React to the {reaction}!"))
        await message.add_reaction(discord.PartialEmoji(name=reaction))
        start = time.perf_counter()
        try:
            _, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                and _reaction.message.channel == ctx.message.channel
                and _reaction.message == message
                and str(_reaction.emoji) == reaction
                and user != ctx.bot.user
                and not user.bot,
                timeout=60,
            )
        except asyncio.TimeoutError:
            return await message.edit(
                embed=discord.Embed(description="No one ate the cookie..."),
            )
        end = time.perf_counter()
        await message.edit(
            embed=discord.Embed(
                description=f"**{user}**  ate the cookie in ```{end - start:.3f}``` seconds!",
            ),
        )
        lis3 = ["1", "2"]
        choice = random.choice(lis3)
        if choice == 2:
            await user.send(
                f"Firstly, Random chose 2 so you get this DM, Secondly, Well Done! You completed it in ```{end - start:.3f}``` seconds.",
            )
        else:
            pass


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Games(bot))
