import os
from asyncio import sleep
from io import FileIO

import discord
from asyncdagpi import ImageFeatures
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class ImageManipulation(commands.Cog, name="Image Manipulation"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dagpi = bot.dagpi
        self.DEFAULT_GIF_LIST_PATH = bot.DEFAULT_GIF_LIST_PATH
        self.description = 'Some fun Image Manipulation Commands'

    @commands.command()
    async def wni(self, ctx, *, name):
        text = f"{name} was not the imposter"
        img = Image.open(FileIO(self.DEFAULT_GIF_LIST_PATH / "amongus.png"))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FileIO(self.DEFAULT_GIF_LIST_PATH / os.path.join("Arial.ttf")), 70)
        draw.text((450, 300), text, font=font, fill="white", align="center")
        img.save("wni.png")
        await ctx.send(file=discord.File("wni.png"))
        await sleep(3)
        os.remove("wni.png")

    @commands.command()
    async def wi(self, ctx, *, name):
        text = f"{name} was the imposter"
        img = Image.open(FileIO(self.DEFAULT_GIF_LIST_PATH / os.path.join("amongus.png")))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FileIO(self.DEFAULT_GIF_LIST_PATH / os.path.join("Arial.ttf")), 60)
        draw.text((450, 300), text, font=font, fill="red", align="right")
        img.save("wi.png")
        await ctx.send(file=discord.File("wi.png"))
        await sleep(3)
        os.remove("wi.png")

    @commands.command()
    async def triggered(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.triggered(), url)
        e2file = discord.File(fp=img.image, filename=f"triggered.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is triggered!")
        e.set_image(url=f"attachment://triggered.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(cooldown_after_parsing=True)
    async def message(self, ctx, member: discord.Member = None, *, text):
        if member is None:
            member = ctx.author

        uname = member.display_name
        text = str(text)
        pfp = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.discord(),
                                                 url=pfp,
                                                 username=uname,
                                                 text=text)
        e2file = discord.File(fp=img.image, filename=f"message.{img.format}")
        e = discord.Embed(title="Here You Go! Message Sent!")
        e.set_image(url=f"attachment://message.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(cooldown_after_parsing=True)
    async def captcha(self, ctx, member: discord.Member = None, *, text):
        if member is None:
            member = ctx.author

        text = str(text)
        textaslen = len(text)
        if textaslen > 13:
            await ctx.send("Maybe text length something smaller then 13?")
        else:
            pfp = str(member.avatar_url_as(format="png", size=1024))
            img = await self.bot.dagpi.image_process(ImageFeatures.captcha(),
                                                     url=pfp,
                                                     text=text)
            e2file = discord.File(
                fp=img.image, filename=f"captcha.{img.format}")
            e = discord.Embed(title="Here You Go! Another Captcha?")
            e.set_image(url=f"attachment://captcha.{img.format}")
            await ctx.send(file=e2file, embed=e)

    @commands.command()
    async def pixel(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.pixel(), url)
        e2file = discord.File(fp=img.image, filename=f"pixel.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is pixel!")
        e.set_image(url=f"attachment://pixel.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command()
    async def jail(self, ctx, member: discord.Member = None):
        """Yes."""
        if member is None:
            member = ctx.author
        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.jail(), url=url)
        e2file = discord.File(fp=img.image, filename=f"jail.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is jail!")
        e.set_image(url=f"attachment://jail.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command()
    async def magik(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.magik(), url)
        e2file = discord.File(fp=img.image, filename=f"magik.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is magik!")
        e.set_image(url=f"attachment://magik.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command()
    async def wanted(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.wanted(), url)
        e2file = discord.File(fp=img.image, filename=f"wanted.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is wanted!")
        e.set_image(url=f"attachment://wanted.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command()
    async def rainbow(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = str(member.avatar_url_as(format="png", size=1024))
        img = await self.bot.dagpi.image_process(ImageFeatures.gay(), url)
        e2file = discord.File(fp=img.image, filename=f"rainbow.{img.format}")
        e = discord.Embed(title="Here You Go! Filter used is gay!")
        e.set_image(url=f"attachment://rainbow.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command()
    async def pan(self, ctx, *, name):
        text = f"Yay! {name} Has come out as pan! :)"
        img = Image.open(FileIO(self.DEFAULT_GIF_LIST_PATH / "pan1.jpg"))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FileIO(self.DEFAULT_GIF_LIST_PATH / "Arial.ttf"), 50)
        draw.text((250, 300), text, font=font, fill="Black", align="center")
        img.save("enby.png")
        await ctx.send(file=discord.File("enby.png"))
        await sleep(3)
        os.remove("enby.png")

    @commands.command()
    async def enby(self, ctx, *, name):
        text = f"Yay! {name} Has come out as enby!"
        img = Image.open(FileIO(self.DEFAULT_GIF_LIST_PATH / "enby1.png"))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FileIO(self.DEFAULT_GIF_LIST_PATH / "Arial.ttf"), 160)
        draw.text((1700, 1100), text, font=font, fill="Black", align="center")
        img.save("enby.png")
        await ctx.send(file=discord.File("enby.png"))
        await sleep(3)
        os.remove("enby.png")

    @commands.command()
    async def bi(self, ctx, *, name):
        text = f"Yay! {name} Has come out as bisexual! \nWell done!"
        img = Image.open(FileIO(self.DEFAULT_GIF_LIST_PATH / "bi1.jfif"))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FileIO(self.DEFAULT_GIF_LIST_PATH / "Arial.ttf"), 14)
        draw.text((30, 85), text, font=font, fill="Black", align="center")
        img.save("bi.png")
        await ctx.send(file=discord.File("bi.png"))
        await sleep(3)
        os.remove("bi.png")


def setup(bot):
    bot.add_cog(ImageManipulation(bot))
