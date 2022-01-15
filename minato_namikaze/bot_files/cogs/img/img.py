import datetime
import os
from asyncio import sleep
from io import FileIO
from typing import Optional, Union

import discord
from asyncdagpi import Client, ImageFeatures
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from ...lib import Tokens, MemberID


class ImageManipulation(commands.Cog, name="Image Manipulation"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dagpi = Client(Tokens.dagpi.value)
        self.DEFAULT_GIF_LIST_PATH = bot.DEFAULT_GIF_LIST_PATH
        self.description = "Some fun Image Manipulation Commands"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{FRAME WITH PICTURE}")

    @commands.command(usage="[member.mention | member.id]")
    async def wni(self, ctx, *, member: Optional[Union[discord.Member, MemberID]]):
        """Prove that you are not sus!"""
        if member == "@everyone":
            await ctx.send(
                f"** {ctx.author.mention} yes yes bro!!! Everyone is not sus!**")
            return
        member = ctx.get_user(member)
        desc = f"** {member}  was not the imposter**"

        file_path = self.DEFAULT_GIF_LIST_PATH / "amoungus_friends.png"
        file = discord.File(file_path)

        embed = discord.Embed(description=desc,
                              timestamp=discord.utils.utcnow())
        embed.set_image(url=f"attachment://{file_path}")
        await ctx.send(file=file, embed=embed)

    @commands.command(usage="[member.mention | member.id]")
    async def wi(self, ctx, *, member: Optional[Union[discord.Member, MemberID]]):
        """Prove anyone that they are sus!"""
        if member == "@everyone":
            desc = f"Hmmmmmmm ** {ctx.author.mention} , Hey guys {ctx.author.mention} is the sus !!!**"
            await ctx.send(desc)
            text = f"{ctx.author.display_name}  is the imposter"
        elif type(member) is discord.Member:
            desc = f"** {member.mention}  is the imposter**"
            text = f"{member.display_name}  is the imposter"
        elif member != "":
            desc = f"** {member}  is the imposter**"
            text = f"{member}  is the imposter"
        else:
            await ctx.send(f"** <@{ctx.author.id}> why you being __sus__ ! **")
            return

        embed = discord.Embed(description=desc,
                              timestamp=discord.utils.utcnow())

        img = Image.open(
            FileIO(self.DEFAULT_GIF_LIST_PATH / os.path.join("amongus.png")))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(
            FileIO(self.DEFAULT_GIF_LIST_PATH / os.path.join("Arial.ttf")), 60)
        draw.text((250, 300), text, font=font, fill="red", align="right")
        img.save("wi.png")
        embed.set_image(url="attachment://wi.png")
        await ctx.send(file=discord.File("wi.png"), embed=embed)
        await sleep(3)
        os.remove("wi.png")

    @commands.command(usage="[member.mention | member.id]")
    async def triggered(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Make anyone triggered"""
        if member is None:
            member = ctx.author

        url = str(member.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.triggered(),
                                                 url)
        e2file = discord.File(fp=img.image, filename=f"triggered.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is triggered!")
        e.set_image(url=f"attachment://triggered.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(cooldown_after_parsing=True, usage="[discord.member.mention.to.send | member.id] <your.message>")
    async def message(self, ctx, member: Optional[Union[discord.Member, MemberID]], *, text):
        """Send a fake Discord message"""
        if member is None:
            member = ctx.author

        uname = member.display_name
        text = str(text)
        pfp = str(member.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.discord(),
                                                 url=pfp,
                                                 username=uname,
                                                 text=text)
        e2file = discord.File(fp=img.image, filename=f"message.{img.format}")
        e = discord.Embed(title="Here You Go! Message Sent!")
        e.set_image(url=f"attachment://message.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(cooldown_after_parsing=True,usage="<member.mention, captcha.text>")
    async def captcha(self, ctx,member: Optional[Union[discord.Member, MemberID]],*, text="Detect Face"):
        """Captcha v3 Image mockup"""
        if member is None:
            member = ctx.author

        text = str(text)
        textaslen = len(text)
        if textaslen > 13:
            await ctx.send("Maybe text length something smaller then 13?")
        else:
            pfp = str(member.avatar.with_format("png").with_size(1024).url)
            img = await self.bot.dagpi.image_process(ImageFeatures.captcha(),
                                                     url=pfp,
                                                     text=text)
            e2file = discord.File(fp=img.image,
                                  filename=f"captcha.{img.format}")
            e = discord.Embed(title="Here You Go! Another Captcha?")
            e.set_image(url=f"attachment://captcha.{img.format}")
            await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def pixel(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Pixallate your pfp"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.pixel(), url)
        e2file = discord.File(fp=img.image, filename=f"pixel.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is pixel!")
        e.set_image(url=f"attachment://pixel.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def jail(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Jail yourself or someone"""
        if member is None:
            member = ctx.author
        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.jail(), url=url)
        e2file = discord.File(fp=img.image, filename=f"jail.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is jail!")
        e.set_image(url=f"attachment://jail.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def wanted(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Get yourself or someone listed in Bingo Book"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.wanted(), url)
        e2file = discord.File(fp=img.image, filename=f"wanted.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is wanted!")
        e.set_image(url=f"attachment://wanted.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def rainbow(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Rainbow light effect"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.gay(), url)
        e2file = discord.File(fp=img.image, filename=f"rainbow.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is gay!")
        e.set_image(url=f"attachment://rainbow.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def gay(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Seperate yourself/others and mark them/yourself as gay!"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.gay(), url)
        e2file = discord.File(fp=img.image, filename=f"gay.{img.format}")
        e = discord.Embed(title="There you go gay!")
        e.set_image(url=f"attachment://gay.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def trash(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Puts trash into trashbin"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(512).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.trash(), url)
        e2file = discord.File(fp=img.image, filename=f"trash.{img.format}")
        e = discord.Embed(title="There you go piece of Trash!")
        e.set_image(url=f"attachment://trash.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(aliases=["delete_trash", "dt"], usage="[member.mention | member.id]")
    async def delete(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Removes trash from bin"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.delete(), url)
        e2file = discord.File(fp=img.image, filename=f"delete.{img.format}")
        e = discord.Embed(title="There you go piece of trash removed!")
        e.set_image(url=f"attachment://delete.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def angel(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Be an Angel"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(512).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.angel(), url)
        e2file = discord.File(fp=img.image, filename=f"angel.{img.format}")
        e = discord.Embed(title="Our dear Angel!")
        e.set_image(url=f"attachment://angel.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def satan(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Be the Devil"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(64).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.satan(), url)
        e2file = discord.File(fp=img.image, filename=f"satan.{img.format}")
        e = discord.Embed(title="Satan!!!")
        e.set_image(url=f"attachment://satan.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(aliases=["chp", "chpaint", "charcoal_paint", "charcoalp"],usage="[member.mention | member.id]")
    async def charcoal(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Get your pfp beautiful charcoal paint"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.charcoal(), url)
        e2file = discord.File(fp=img.image, filename=f"charcoal.{img.format}")
        e = discord.Embed(title="There you go your lovely charcoal paintaing")
        e.set_image(url=f"attachment://charcoal.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def hitler(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Hail Hitler"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(64).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.hitler(), url)
        e2file = discord.File(fp=img.image, filename=f"hitler.{img.format}")
        e = discord.Embed(title="Worse than Hitler!!!")
        e.set_image(url=f"attachment://hitler.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def wasted(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """GTA V wasted screen"""
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.wasted(), url)
        e2file = discord.File(fp=img.image, filename=f"wasted.{img.format}")
        e = discord.Embed(title="Wasted! :skull_crossbones:")
        e.set_image(url=f"attachment://wasted.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def bomb(self, ctx, member: Optional[Union[discord.Member, MemberID]]):
        """Bomb someone"""
        e = discord.Embed(title="Boooom! :skull_crossbones:")
        if member is None:
            member = ctx.author

        url = str(member.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.bomb(), url)
        e2file = discord.File(fp=img.image, filename=f"bomb.{img.format}")
        e.set_image(url=f"attachment://bomb.{img.format}")
        await ctx.send(embed=e, file=e2file)


def setup(bot):
    bot.add_cog(ImageManipulation(bot))
