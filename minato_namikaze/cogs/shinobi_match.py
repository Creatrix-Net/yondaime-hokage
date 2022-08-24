import asyncio
import random
from typing import TYPE_CHECKING, List, Union

import aiohttp
import discord
import orjson
from discord.ext import commands
from minato_namikaze.lib import (
    Characters,
    LinksAndVars,
    MatchHandlerView,
    MemberID,
    ShinobiMatchCharacterSelection,
    cache,
    Embed,
    ErrorEmbed,
)

if TYPE_CHECKING:
    from minato_namikaze.lib import Context
    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class ShinobiMatchCog(commands.Cog, name="Shinobi Match"):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.description = "An amazing shinobi match with your friends"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f5e1")

    @staticmethod
    @cache()
    async def characters_data(ctx: "Context") -> List[Characters]:
        async with aiohttp.ClientSession() as session, session.get(
            LinksAndVars.character_data.value
        ) as resp:
            character_data: dict = orjson.loads(await resp.text())
        return [
            Characters.from_record(character_data[i], ctx, i) for i in character_data
        ]

    @classmethod
    async def return_random_characters(self, ctx: "Context") -> List[Characters]:
        characters_data = await self.characters_data(ctx)
        random.shuffle(characters_data)
        return random.sample(characters_data, 25)

    @staticmethod
    def return_select_help_embed(author: discord.Member):
        embed = Embed(
            title="Select your character",
            description="```\nSelect your character using which you will fight\n```\n Use to `dropdown` below to view the characters available and click the `confirm` button to confirm your character",
        )
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        return embed

    @commands.command(
        usage="<opponent.mention>",
        aliases=["shinobi_match", "matchwith", "shinobimatch", "match_with"],
    )
    async def match(self, ctx: "Context", opponent: Union[discord.Member, MemberID]):
        """
        Play shinobi match with your friends using the characters from `Naruto Verse`

        **Steps**
        > 1. Type `{prefix}match @player_mention`
        > 2. Then both player selects the character from their respection selection boxes
        > 3. Then starts the amazing match!

        **Rules**
        > 1. You cannot repeat a move `twice` in a row
        > 2. You will have only `2 Special Moves` to perform, so use wisely
        > 3. `On timeout`, by the default the user with high health value would be decalred as a winner
        > 4. Also you can perform `healing operations twice` in the whole game, so use the heal wisely.
        """

        if opponent is ctx.author or opponent.bot:
            await ctx.send(
                embed=ErrorEmbed(
                    description="*You cannot play this game yourself or with a bot*"
                )
            )
            return

        view1 = ShinobiMatchCharacterSelection(
            characters_data=await self.return_random_characters(ctx),
            player=ctx.author,
            ctx=ctx,
        )
        select_msg1: discord.Message = await ctx.send(
            embed=self.return_select_help_embed(ctx.author), view=view1
        )

        view2 = ShinobiMatchCharacterSelection(
            characters_data=await self.return_random_characters(ctx),
            player=opponent,
            ctx=ctx,
        )
        select_msg2: discord.Message = await ctx.send(
            embed=self.return_select_help_embed(opponent), view=view2
        )

        await view1.wait()
        await view2.wait()

        if view1.character is None or view2.character is None:
            return await ctx.send(
                embed=ErrorEmbed(
                    title="One of the shinobi didn't choose his character on time."
                )
            )

        await select_msg1.delete()
        await select_msg2.delete()

        timer = await ctx.send("Starting the match in `3 seconds`")
        for i in range(1, 3):
            await timer.edit(f"Starting the match in `{3-i} seconds`")
            await asyncio.sleep(1)
        await timer.delete()

        view = MatchHandlerView(
            player1=(ctx.author, view1.character), player2=(opponent, view2.character)
        )
        view.message = await ctx.send(
            content=f"{ctx.author.mention} now your turn",
            embed=view.make_embed(),
            view=view,
        )


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(ShinobiMatchCog(bot))
