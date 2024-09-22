from __future__ import annotations

import asyncio
import functools
import os
import sys
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING
from typing import Union

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageSequence
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import String

from minato_namikaze.lib import Badge
from minato_namikaze.lib import Badges as BadgesDBHandler
from minato_namikaze.lib import Base
from minato_namikaze.lib import BASE_DIR
from minato_namikaze.lib import EmbedPaginator
from minato_namikaze.lib import generate
from minato_namikaze.lib import ImageWriter
from minato_namikaze.lib import session_obj
from minato_namikaze.lib import StarboardEmbed
from minato_namikaze.lib import Tokens
from minato_namikaze.lib import Webhooks

if TYPE_CHECKING:
    from lib import Context

    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class Badges(Base):
    __tablename__ = "badges"
    __table_args__ = {"extend_existing": True}

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    badge_name = Column(String(250), nullable=False, index=True, unique=True)
    code = Column(String(20), nullable=False, index=True, unique=True)
    file_name = Column(String(500), nullable=False, index=True, unique=True)
    is_inverted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        unique=True,
    )


def check_if_it_is_me(interaction: discord.Interaction) -> bool:
    """Check if the inetractions's users is the bot user

    :return: True or False depending on the result
    :rtype: bool
    """
    return interaction.user.id == interaction.client.owner_id


def get_badge_code(badge_name: str) -> str:
    """Returns the badge code from its name

    :param badge_name: The name of the badge image
    :type badge_name: str
    :return: Badge Code
    :rtype: str
    """
    return "".join([i[0].upper() for i in badge_name.split(" ")])


@app_commands.command()
@app_commands.describe(name="The name of the badge")
@app_commands.describe(file="The raw badge image containing the badge")
@app_commands.check(check_if_it_is_me)
async def add_new_badge(
    interaction: discord.Interaction,
    name: str,
    file: discord.Attachment,
):
    """Adds a new badge to database"""
    if not file.content_type.startswith("image"):
        await interaction.response.send_message(
            f"{file.filename} is not a valid image",
            ephemeral=True,
        )
        return
    embed = StarboardEmbed(title=name.title())
    embed.set_image(url=f"attachment://{file.filename}")
    async with aiohttp.ClientSession() as session:
        wh = discord.Webhook.from_url(
            Webhooks.badges.value,
            session=session,
            bot_token=Tokens.token.value,
        )
        sent_message: discord.WebhookMessage = await wh.send(
            wait=True,
            embed=embed,
            file=await file.to_file(
                use_cached=True,
                description=f"{file.filename.title()} raw badge data.",
            ),
        )
    badge_object = Badges(
        id=sent_message.id,
        badge_name=name.title(),
        file_name=sent_message.embeds[0].image.url,
        code=get_badge_code(name),
    )
    async with session_obj() as session, session.begin():
        session.add(badge_object)
    await interaction.response.send_message(
        f"Added, {sent_message.jump_url}",
        ephemeral=True,
    )


class BadgesPageEntry:
    __slots__ = ("code", "name", "file", "embed")

    def __init__(self, entry: Mapping):
        self.code = entry["code"]
        self.name = entry["badge_name"]
        self.file: discord.Attachment = entry["file_name"]
        self.embed = StarboardEmbed(
            title=self.name,
            description=f"BADGE CODE: `{self.code}`",
        )
        self.embed.set_image(url=entry["file_name"].url)

    def __str__(self):
        return f"{self.name} (CODE: {self.code})"


class BadgesCog(commands.Cog, name="Badges"):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Create fun fake badges based on your discord profile"

    async def cog_load(self):
        self.bot.tree.add_command(add_new_badge)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f9a1")

    @staticmethod
    def remove_white_barcode(img: Image) -> Image:
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        return img

    @staticmethod
    def invert_barcode(img: Image) -> Image:
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255))
            else:
                newData.append(item)

        img.putdata(newData)
        return img

    @staticmethod
    async def dl_image(url: str) -> BytesIO:
        """Download bytes like object of user avatar"""
        async with aiohttp.ClientSession() as session, session.get(str(url)) as resp:
            test = await resp.read()
            return BytesIO(test)

    def make_template(
        self,
        user: discord.User | discord.Member,
        badge: Badge,
        template: Image,
    ) -> Image:
        """Build the base template before determining animated or not"""
        if hasattr(user, "roles"):
            department = (
                "GENERAL SUPPORT"
                if user.top_role.name == "@everyone"
                else user.top_role.name.upper()
            )
            status = user.status
            level = str(len(user.roles))
        else:
            department = "GENERAL SUPPORT"
            status = "online"
            level = "1"
        if str(status) == "online":
            status = "ACTIVE"
        if str(status) == "offline":
            status = "COMPLETING TASK"
        if str(status) == "idle":
            status = "AWAITING INSTRUCTIONS"
        if str(status) == "dnd":
            status = "MIA"
        barcode = BytesIO()
        generate("code39", str(user.id), writer=ImageWriter(self), output=barcode)
        barcode = Image.open(barcode)
        barcode = self.remove_white_barcode(barcode)
        fill = (0, 0, 0)  # text colour fill
        if badge.is_inverted:
            fill = (255, 255, 255)
            barcode = self.invert_barcode(barcode)
        template = Image.open(template)
        template = template.convert("RGBA")
        barcode = barcode.convert("RGBA")
        barcode = barcode.resize((555, 125), Image.ANTIALIAS)
        template.paste(barcode, (400, 520), barcode)
        # font for user information
        font_loc = str(BASE_DIR / os.path.join("lib", "data", "arial.ttf"))
        try:
            font1 = ImageFont.truetype(font_loc, 30)
            font2 = ImageFont.truetype(font_loc, 24)
        except Exception as e:
            font1 = None
            font2 = None
        # font for extra information

        draw = ImageDraw.Draw(template)
        # adds username
        draw.text((225, 330), str(user.display_name), fill=fill, font=font1)
        # adds ID Class
        draw.text(
            (225, 400),
            badge.code + "-" + str(user).split("#")[1],
            fill=fill,
            font=font1,
        )
        # adds user id
        draw.text((250, 115), str(user.id), fill=fill, font=font2)
        # adds user status
        draw.text((250, 175), status, fill=fill, font=font2)
        # adds department from top role
        draw.text((250, 235), department, fill=fill, font=font2)
        # adds user level
        draw.text((420, 475), "LEVEL " + level, fill="red", font=font1)
        # adds user level
        if badge.badge_name != "discord" and user is discord.Member:
            draw.text((60, 585), str(user.joined_at), fill=fill, font=font2)
        else:
            draw.text((60, 585), str(user.created_at), fill=fill, font=font2)
        barcode.close()
        return template

    @staticmethod
    def make_animated_gif(template: Image, avatar: BytesIO) -> BytesIO:
        """Create animated badge from gif avatar"""
        gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
        img_list = []
        num = 0
        for frame in gif_list:
            temp2 = template.copy()
            watermark = frame.copy()
            watermark = watermark.convert("RGBA")
            watermark = watermark.resize((100, 100))
            watermark.putalpha(128)
            id_image = frame.resize((165, 165))
            temp2.paste(watermark, (845, 45, 945, 145), watermark)
            temp2.paste(id_image, (60, 95, 225, 260))
            temp2.thumbnail((500, 339), Image.ANTIALIAS)
            img_list.append(temp2)
            num += 1
            temp = BytesIO()

            temp2.save(
                temp,
                format="GIF",
                save_all=True,
                append_images=img_list,
                duration=0,
                loop=0,
            )
            temp.name = "temp.gif"
            if sys.getsizeof(temp) > 7000000 and sys.getsizeof(temp) < 8000000:
                break
        return temp

    @staticmethod
    def make_badge(template: Image, avatar: Image):
        """Create basic badge from regular avatar"""
        watermark = avatar.convert("RGBA")
        watermark.putalpha(128)
        watermark = watermark.resize((100, 100))
        id_image = avatar.resize((165, 165))
        template.paste(watermark, (845, 45, 945, 145), watermark)
        template.paste(id_image, (60, 95, 225, 260))
        temp = BytesIO()
        template.save(temp, format="PNG")
        temp.name = "temp.gif"
        return temp

    async def create_badge(self, user, badge, is_gif: bool):
        """Async create badges handler"""
        template_img = await self.dl_image(badge.file_name)
        task = functools.partial(
            self.make_template,
            user=user,
            badge=badge,
            template=template_img,
        )
        task = self.bot.loop.run_in_executor(None, task)
        try:
            template = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return
        if user.display_avatar.is_animated() and is_gif:
            url = user.display_avatar.with_format("gif")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(
                self.make_animated_gif,
                template=template,
                avatar=avatar,
            )
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        else:
            url = user.display_avatar.with_format("png")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(self.make_badge, template=template, avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        temp.seek(0)
        return temp

    @staticmethod
    async def get_badge(badge_name: str, ctx: Context) -> Badge:
        all_badges = await BadgesDBHandler(ctx).get_all_badges()
        to_return = None
        for badge in all_badges:
            if (
                badge_name.lower() in badge["badge_name"].lower()
                or badge_name.lower() in badge["code"].lower()
            ):
                to_return = await Badge.from_json(badge)
        return to_return

    @commands.hybrid_command(aliases=["badge"])
    async def badges(self, ctx: Context, *, badge: str) -> None:
        """
        Creates a fun fake badge based on your discord profile
        `badge` is the name of the badges
        do `[p]listbadges` to see available badges
        """
        user = ctx.message.author
        if badge.lower() == "list":
            await ctx.invoke(self.listbadges)
            return
        badge_obj = await self.get_badge(badge, ctx)
        if not badge_obj:
            await ctx.send(f"`{badge}` is not an available badge.")
            return
        async with ctx.channel.typing():
            badge_img = await self.create_badge(user, badge_obj, False)
            if badge_img is None:
                await ctx.send("Something went wrong sorry!")
                return
            image = discord.File(badge_img, "badge.png")
            embed = discord.Embed(color=ctx.author.color)
            embed.set_image(url="attachment://badge.png")
            badge_img.close()
            await ctx.send(files=[image])

    @commands.hybrid_command(aliases=["gbadge", "gifbadge"])
    async def gbadges(self, ctx: Context, *, badge: str) -> None:
        """
        Creates a fun fake gif badge based on your discord profile
        this only works if you have a gif avatar
        `badge` is the name of the badges
        do `[p]listbadges` to see available badges
        """
        user = ctx.message.author
        if badge.lower() == "list":
            await ctx.invoke(self.listbadges)
            return
        badge_obj = await self.get_badge(badge, ctx)
        if not badge_obj:
            await ctx.send(f"`{badge}` is not an available badge.")
            return
        async with ctx.channel.typing():
            badge_img = await self.create_badge(user, badge_obj, True)
            if badge_img is None:
                await ctx.send("Something went wrong sorry!")
                return
            image = discord.File(badge_img)
            badge_img.close()
            await ctx.send(file=image)

    @commands.hybrid_command()
    async def listbadges(self, ctx: Context) -> None:
        """
        List the available badges that can be created
        """
        global_badges = await BadgesDBHandler(ctx).get_all_badges()
        print(global_badges)
        embed_paginator = EmbedPaginator(
            entries=[BadgesPageEntry(i).embed for i in global_badges],
            ctx=ctx,
        )
        await embed_paginator.start()


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(BadgesCog(bot))
