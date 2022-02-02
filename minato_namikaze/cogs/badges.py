import asyncio
import functools
import os
import sys
from io import BytesIO
from typing import Union

import aiohttp
import discord
from discord.ext import commands
from lib import BASE_DIR, Badge, Badges, ImageWriter, SimplePages, generate
from PIL import Image, ImageDraw, ImageFont, ImageSequence


class BadgesPageEntry:
    __slots__ = ("code", "name")

    def __init__(self, entry):
        self.code = entry["code"]
        self.name = entry["badge_name"]

    def __str__(self):
        return f"{self.name} (CODE: {self.code})"


class BadgePages(SimplePages):
    def __init__(self, entries, *, ctx: commands.Context, per_page: int = 5):
        converted = [BadgesPageEntry(entry) for entry in entries]
        super().__init__(converted, per_page=per_page, ctx=ctx)


class BadgesCog(commands.Cog, name="Badges"):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Create fun fake badges based on your discord profile"

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
        async with aiohttp.ClientSession() as session, session.get(
                str(url)) as resp:
            test = await resp.read()
            return BytesIO(test)

    def make_template(self, user: Union[discord.User, discord.Member],
                      badge: Badge, template: Image) -> Image:
        """Build the base template before determining animated or not"""
        if hasattr(user, "roles"):
            department = ("GENERAL SUPPORT" if user.top_role.name
                          == "@everyone" else user.top_role.name.upper())
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
        generate("code39",
                 str(user.id),
                 writer=ImageWriter(self),
                 output=barcode)
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
        task = functools.partial(self.make_template,
                                 user=user,
                                 badge=badge,
                                 template=template_img)
        task = self.bot.loop.run_in_executor(None, task)
        try:
            template = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return
        if user.display_avatar.is_animated() and is_gif:
            url = user.display_avatar.with_format("gif")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(self.make_animated_gif,
                                     template=template,
                                     avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        else:
            url = user.display_avatar.with_format("png")
            avatar = Image.open(await self.dl_image(url))
            task = functools.partial(self.make_badge,
                                     template=template,
                                     avatar=avatar)
            task = self.bot.loop.run_in_executor(None, task)
            try:
                temp = await asyncio.wait_for(task, timeout=60)
            except asyncio.TimeoutError:
                return

        temp.seek(0)
        return temp

    async def get_badge(self, badge_name: str, ctx) -> Badge:
        all_badges = await Badges(ctx).get_all_badges()
        to_return = None
        for badge in all_badges:
            if (badge_name.lower() in badge["badge_name"].lower()
                    or badge_name.lower() in badge["code"].lower()):
                to_return = await Badge.from_json(badge)
        return to_return

    @commands.command(aliases=["badge"])
    async def badges(self, ctx: commands.Context, *, badge: str) -> None:
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
            await ctx.send("`{}` is not an available badge.".format(badge))
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

    @commands.command(aliases=["gbadge"])
    async def gbadges(self, ctx: commands.Context, *, badge: str) -> None:
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
            await ctx.send("`{}` is not an available badge.".format(badge))
            return
        async with ctx.channel.typing():
            badge_img = await self.create_badge(user, badge_obj, True)
            if badge_img is None:
                await ctx.send("Something went wrong sorry!")
                return
            image = discord.File(badge_img)
            badge_img.close()
            await ctx.send(file=image)

    @commands.command()
    async def listbadges(self, ctx: commands.Context) -> None:
        """
        List the available badges that can be created
        """
        global_badges = await Badges(ctx).get_all_badges()
        embed_paginator = BadgePages(ctx=ctx, entries=global_badges)
        await embed_paginator.start()


def setup(bot):
    bot.add_cog(BadgesCog(bot))
