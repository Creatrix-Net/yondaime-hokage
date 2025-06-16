from __future__ import annotations

import json
import time
from asyncio import TimeoutError
from datetime import timedelta
from json.decoder import JSONDecodeError
from random import choice
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext import tasks
from discord.ext.commands import Cog
from discord.ext.commands import command
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy_utils import URLType

from minato_namikaze.lib import Base
from minato_namikaze.lib import cache
from minato_namikaze.lib import convert
from minato_namikaze.lib import Embed
from minato_namikaze.lib import format_relative
from minato_namikaze.lib import FutureTime
from minato_namikaze.lib import GiveawayConfig
from minato_namikaze.lib import is_mod
from minato_namikaze.lib import LinksAndVars
from minato_namikaze.lib import SuccessEmbed

if TYPE_CHECKING:
    from lib import Context

    from .. import MinatoNamikazeBot

import logging

log = logging.getLogger(__name__)


class Giveaways(Base):
    __tablename__ = "giveaways"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, index=True, primary_key=True)
    expires = Column(DateTime, index=True, nullable=False)
    server_id = Column(BigInteger, index=True, nullable=False)
    jump_url = Column(URLType, nullable=False, index=True)
    image_url = Column(
        URLType,
        default=LinksAndVars.giveaway_image.value,
        nullable=False,
    )
    giveaway_deleted = Column(Boolean, default=True, nullable=False)


class Giveaway(Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Helps you to organise a simple giveaway."
        self.giveaway_image = LinksAndVars.giveaway_image.value
        self.declare_results.start()

    @cache()
    async def get_giveaway_config(
        self,
        giveaway_id: discord.Message,
    ):
        return await GiveawayConfig.from_record(giveaway_id, self.bot)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{PARTY POPPER}")

    async def create_timer_for_giveaway(
        self,
        giveaway_id: discord.Message,
        time_ends: int | FutureTime | float,
    ) -> None:
        """Creates the timer for the giveaway

        :param giveaway_id: Giveaway id
        :type giveaway_id: discord.Message
        :param time_ends: Time when the giveaway will end
        :type time_ends: Union[int, FutureTime]
        """
        database = await self.database_class()
        await database.set(giveaway_id.id, [int(time_ends), giveaway_id.jump_url])

    @tasks.loop(minutes=30, reconnect=True)
    async def declare_results(self):
        database = await self.database_class()
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                try:
                    giveaway_message = await commands.MessageConverter().convert(
                        await self.bot.get_context(message),
                        data[data_keys[0]][1],
                    )
                    timestamp = data[data_keys[0]][0]
                    if discord.utils.utcnow().timestamp() >= int(timestamp):
                        winner = await self.determine_winner(giveaway_message, self.bot)
                        await giveaway_message.channel.send(
                            f"\U0001f389 Congratulations **{winner.mention}** on winning the Giveaway \U0001f389",
                            reference=giveaway_message,
                        )
                        await message.delete()
                        self.get_giveaway_config.invalidate(self, giveaway_message.id)
                except (
                    commands.ChannelNotFound,
                    commands.MessageNotFound,
                    commands.ChannelNotReadable,
                ):
                    await message.delete()
            except JSONDecodeError:
                await message.delete()

    @command(
        name="giveaway",
        aliases=["gcreate", "gcr", "giftcr"],
    )
    @commands.guild_only()
    @is_mod()
    async def create_giveaway(self, ctx: Context):
        """Allowes you to to create giveaway by answering some simple questions!"""
        # Ask Questions
        embed = Embed(
            title="Giveaway Time!! \U00002728",
            description="Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway",
            color=ctx.author.color,
        )
        await ctx.send(embed=embed)
        questions = [
            "In Which channel do you want to host the giveaway?",
            "For How long should the Giveaway be hosted ? type number followed (s|m|h|d)",
            "What is the Prize?",
            "What role should a person must have in order to enter? If no roles required then type `none`",
            "Tasks that the person should do in order to participate? If no tasks then type `none`",
        ]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}", description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for("message", timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)

        # Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send(
                f"The Channel provided was wrong. The channel provided should be like {ctx.channel.mention}",
            )
            return

        channel = self.bot.get_channel(channel_id)

        # Check if the role is valid
        role = answers[3]
        if role.lower() in ("none", "no", "no roles"):
            role = None
        else:
            try:
                int(answers[3][3:-1])
            except:
                i = ctx.guild.roles
                for j in i:
                    if j.name in ("@everyone", "@here"):
                        i.remove(j)
                bot_roles = choice(i)
                await ctx.send(
                    f"The role provided was wrong. The role should be like {bot_roles.mention}",
                )
                return

        time_ends = convert(answers[1]) * 1000

        # Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        if time == -2:
            await ctx.send("The Time was not conventional number")
            return
        prize = answers[2]

        task = answers[4]
        if task.lower() in ("none", "no", "no task"):
            task = None

        embed = Embed(
            title="**:tada::tada: Giveaway Time !! :tada::tada:**",
            description=f":gift: Win a **{prize}** today",
            colour=0x00FFFF,
        )
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.display_avatar.url,
        )
        embed.set_image(url=self.giveaway_image)
        embed.add_field(
            name="Giveway ends in",
            value=f"{format_relative(discord.utils.utcnow() + timedelta(milliseconds=time_ends))} | [Timer]({LinksAndVars.website.value}/giveaway_timer.html?start={int(time.time() * 1000)}&length={time_ends})",
        )
        if role:
            embed.add_field(name="Role Required", value=f"{role}")
        if task:
            embed.add_field(name="\U0001f3c1 Tasks", value=task)
        newMsg = await channel.send(embed=embed)
        embed.set_footer(text=f"Giveaway ID: {newMsg.id}")
        await newMsg.edit(embed=embed)
        await newMsg.add_reaction(discord.PartialEmoji(name="\U0001f389"))
        await ctx.send(
            f"Your giveaway will be hosted in {channel.mention} and will last for {answers[1]}\n{newMsg.jump_url}",
        )
        await self.create_timer_for_giveaway(
            newMsg,
            (discord.utils.utcnow() + timedelta(milliseconds=time_ends)).timestamp(),
        )

    async def determine_winner(
        self,
        giveaway_id: discord.Message,
        bot: MinatoNamikazeBot,
    ) -> str | discord.Member:
        """Determines winner

        :param giveaway_id: The giveaway id
        :type giveaway_id: discord.Message
        :param bot: The bot class
        :type bot: commands.Bot
        :return: The winner details
        :rtype: Union[str, discord.Member]
        """
        reactions = discord.utils.find(
            lambda a: str(a) == str(discord.PartialEmoji(name="\U0001f389")),
            giveaway_id.reactions,
        )
        if reactions is None:
            return "The channel or ID mentioned was incorrect"
        try:
            giveaway_config = await self.get_giveaway_config(
                giveaway_id.id if not isinstance(giveaway_id.id, int) else giveaway_id,
            )
        except AttributeError as e:
            return str(e)

        reacted_users = await reactions.users().flatten()
        if discord.utils.get(reacted_users, id=bot.application_id):
            reacted_users.remove(
                discord.utils.get(reacted_users, id=bot.application_id),
            )
        if giveaway_config.role_required is not None and len(reacted_users) <= 0:
            reacted_users = list(
                filter(
                    lambda a: discord.utils.get(
                        a.roles,
                        id=int(
                            giveaway_config.role_required.lstrip("<@&")
                            .lstrip("<&")
                            .rstrip(">"),
                        ),
                    )
                    is not None,
                    reacted_users,
                ),
            )
        if len(reacted_users) <= 0:
            emptyEmbed = Embed(
                title="\U0001f389\U0001f389 Giveaway Time !! \U0001f389\U0001f389",
                description="\U0001f381 Win a Prize today",
            )
            emptyEmbed.set_author(
                name=giveaway_config.host.display_name,
                icon_url=giveaway_config.host.display_avatar.url,
            )
            emptyEmbed.add_field(
                name="No winners",
                value="Not enough participants to determine the winners",
            )
            emptyEmbed.set_image(url=self.giveaway_image)
            emptyEmbed.set_footer(text="No one won the Giveaway")
            await giveaway_id.edit(embed=emptyEmbed)
            return f"No one won the giveaway! As there were not enough participants!\n{giveaway_config.jump_url}"
        winner = choice(reacted_users)
        winnerEmbed = giveaway_config.embed
        if (
            discord.utils.find(
                lambda a: a["name"].lower() == "\U0001f389 Winner \U0001f389".lower(),
                giveaway_config.embed_dict["fields"],
            )
            is None
        ):
            winnerEmbed.add_field(
                name="\U0001f389 Winner \U0001f389",
                value=winner.mention,
                inline=False,
            )
        await giveaway_id.edit(embed=winnerEmbed)
        return winner

    @command(
        name="giftrrl",
        usage="<giveaway id> [channel]",
        aliases=[
            "gifreroll",
            "gftroll",
            "grr",
            "giftroll",
            "giveawayroll",
            "giveaway_roll",
            "reroll",
        ],
    )
    @is_mod()
    @commands.guild_only()
    async def giveaway_reroll(
        self,
        ctx: Context,
        giveaway_id: commands.MessageConverter | discord.Message,
    ):
        """
        It picks out the giveaway winners
        `Note: It dosen't checks for task, It only checks for roles if specified`
        """
        if not await ctx.prompt(
            f"Do you really want to **reroll or declare the results for** giveaway with id **{giveaway_id.id}**, hosted in {giveaway_id.channel.mention}?",
        ):
            return
        channel = giveaway_id.channel
        winner = await self.determine_winner(giveaway_id, ctx.bot)
        if isinstance(winner, str):
            return await ctx.send(winner)
        await channel.send(
            f"\U0001f389 Congratulations **{winner.mention}** on winning the Giveaway \U0001f389",
            reference=giveaway_id,
        )
        await ctx.send(giveaway_id.jump_url)
        self.get_giveaway_config.invalidate(self, giveaway_id.id)

    @command(
        name="giftdel",
        usage="<giveaway id>",
        aliases=["gifdel", "gftdel", "gdl"],
    )
    @is_mod()
    @commands.guild_only()
    async def giveaway_stop(
        self,
        ctx: Context,
        giveaway_id: commands.MessageConverter | discord.Message,
    ):
        """
        Cancels the specified giveaway
        `Note: This also deletes that giveaway message`
        """
        if not await ctx.prompt(
            f"Do you really want to **stop/delete** the giveaway with id **{giveaway_id.id}** hosted in {giveaway_id.channel.mention}?\n`Note: This action is irreversible!`",
        ):
            return
        z
        database = await self.database_class()
        await database.delete(giveaway_id.id)
        await giveaway_id.delete()
        self.get_giveaway_config.invalidate(self, giveaway_id.id)
        await ctx.send(
            embed=SuccessEmbed(
                title=f"The giveaway with id {giveaway_id.id} deleted successfully!",
            ),
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> None:
        if payload.guild_id is None:
            return
        reaction = str(payload.emoji)
        if reaction != str(discord.PartialEmoji(name="\U0001f389")):
            return

        if payload.user_id == self.bot.application_id:
            return

        msg = await (await self.bot.fetch_channel(payload.channel_id)).fetch_message(
            payload.message_id,
        )
        try:
            giveaway_config = await self.get_giveaway_config(payload.message_id)
        except AttributeError:
            return

        if giveaway_config.role_required is None:
            return
        role_present = discord.utils.get(
            payload.member.roles,
            id=int(
                giveaway_config.role_required.lstrip("<@&").lstrip("<&").rstrip(">"),
            ),
        )
        if role_present is None:
            try:
                await msg.remove_reaction(
                    discord.PartialEmoji(name="\U0001f389"),
                    payload.member,
                )
                await payload.member.send(
                    "\U000026a0 Sorry you don't have the required roles in order to enter the giveaway :(",
                )
            except (
                discord.HTTPException,
                discord.Forbidden,
                discord.InvalidArgument,
                discord.NotFound,
            ):
                pass


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Giveaway(bot))
