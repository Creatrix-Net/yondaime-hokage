# Future Imports
from __future__ import annotations

import asyncio
import io
import os
import platform
from random import choice
from typing import Optional, Union

import discord
from pyppeteer import launch
import pyppeteer
import mystbin
from asyncdagpi import ImageFeatures
from discord.ext import commands, owoify
from gtts import gTTS
from PIL import Image

from ...lib import Embed, LinksAndVars, TimeConverter


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Some random fun and usefull commands."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{GAME DIE}")

    @commands.command(aliases=["takeitback"], usage="<member.mention>")
    async def insult(self,
                     ctx,
                     user: Optional[Union[int, discord.Member]] = None):
        """
        Insult a user
        `user` the user you would like to insult
        """
        if user:
            user = ctx.get_user(user)
            if user.id == self.bot.user.id:
                user = ctx.message.author
                bot_msg = [
                    " How original. No one else had thought of trying to **get the bot to insult itself**. \nI applaud your creativity. \nYawn. **Perhaps this is why you don't have friends**. \n\nYou don't add anything new to any conversation. \n**You are more of a bot than me, predictable answers, and absolutely dull to have an actual conversation with.**",
                    "Just remember I am **Konohagakure Yellow Falsh** and **Konohagakure FOURTH HOKAGE**",
                ]
                e = Embed(title=":warning:", description=choice(bot_msg))
                e.set_image(url="https://i.imgur.com/45CUkfq.jpeg")
                await ctx.send(ctx.author.mention, embed=e)

            else:
                await ctx.send(
                    f"{user.mention} was **insulted** by {ctx.message.author.mention}",
                    embed=Embed(title=":warning:",
                                description=choice(
                                    LinksAndVars.insults.value)),
                )
        else:
            await ctx.send(
                ctx.message.author.mention,
                embed=Embed(title=":warning:",
                            description=choice(LinksAndVars.insults.value)),
            )

    @commands.command(usage="{text}")
    async def owoify(self, ctx, text):
        """Owoify the message"""
        lol = owoify.owoify(f"{text}")
        await ctx.send(lol)

    @commands.command()
    @commands.cooldown(1, 40, commands.BucketType.guild)
    async def magic(self, ctx, user: discord.Member = None):
        """See magic!"""
        user = user or ctx.author
        url = str(user.avatar.with_format("png").with_size(1024).url)
        img = await self.bot.dagpi.image_process(ImageFeatures.magik(), url)
        e2file = discord.File(fp=img.image, filename=f"magik.{img.format}")
        e = Embed(title="Magik!")
        e.set_image(url=f"attachment://magik.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command()
    @commands.cooldown(1, 40, commands.BucketType.guild)
    async def qr(self, ctx, colour="255-255-255", *, url=None):
        """Generates easy QR Code"""
        colours = {
            "255-255-255": "255-255-255",
            "black": "0-0-0",
            "red": "FF0000",
            "blue": "00f",
        }
        col = ["black", "red", "blue"]
        if colour == "255-255-255":
            col = ["255-255-255", "red", "blue"]
        e = Embed(title="Here you go, Made qr code!")
        msg = await ctx.send("Creating!")

        if colour in col:
            yes = colours[colour]
            url1 = url.replace(" ", "+")
            qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url1}&bgcolor={yes}"
            e.set_image(url=qr)
            await msg.edit(content="", embed=e)

        else:
            if not colour in col:
                if url is None:
                    url = ""
                colour = f"{colour} {url}"
                colour1 = colour.replace(" ", "+")
                qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={colour1}"
                e.set_image(url=qr)
                await msg.edit(content="", embed=e)
            else:
                pass

    @commands.command(
        usage="<time> <reminder> (Time needs to be in seconds...)")
    async def remind(self, ctx, time: TimeConverter, *, reminder):
        """A simple reminder"""
        if int(time) < 12 * 60 * 60:
            e = Embed(
                title="I will remind you!",
                descripition=f"I will you remind you in {int(time)/3600} minutes!",
            )
            await ctx.send(embed=e)
            await asyncio.sleep(int(time))
            e2 = Embed(
                title=f"Hello {ctx.author}",
                description=f"I have come to remind you to {reminder}!",
            )
            await ctx.message.reply(embed=e2)
        else:
            await ctx.send(
                "Please give a reminder time less than 12 hours, I cannot remember for that long!"
            )

    @commands.command(usage="<name>")
    async def sn(self, ctx, *, name):
        """Introduce yourself to everyone"""
        tts = gTTS(text=f"Hi! {name} is really cool!", lang="en")
        tts.save("announce.mp3")
        await ctx.send(file=discord.File("announce.mp3"))
        await asyncio.sleep(5)
        os.remove("announce.mp3")

    @commands.command(usage="<text>")
    async def tts(self, ctx, *, text):
        """Generate text to speech messages"""
        lol = gTTS(text=f"{text}")
        lol.save("tts.mp3")
        await ctx.send(file=discord.File("tts.mp3"))
        await asyncio.sleep(5)
        os.remove("tts.mp3")

    @commands.command(aliases=["color", "colour", "sc"],
                      usage="<hexadecimal colour code>")
    async def show_color(self, ctx, *, color: discord.Colour):
        """Enter a color and you will see it!"""
        file = io.BytesIO()
        Image.new("RGB", (200, 90), color.to_rgb()).save(file, format="PNG")
        file.seek(0)
        em = Embed(color=color, title=f"Showing Color: {str(color)}")
        em.set_image(url="attachment://color.png")
        await ctx.send(file=discord.File(file, "color.png"), embed=em)

    @commands.command(aliases=["myst"], usage="<code>/<text>")
    async def mystbin(self, ctx, *, text):
        """Generate an Mystbin for yourself"""
        paste = await self.bot.mystbin_client.post(f"{text}", syntax="python")
        e = discord.Embed(
            title="I have created a mystbin link for you!",
            description=f"[Click Here]({paste.url})",
        )
        await ctx.send(embed=e)

    @commands.command(aliases=["getmyst"], usage="<mystbin_id>")
    async def getmystbin(self, ctx, id):
        """Get your Mystbi using your id"""
        try:
            get_paste = await self.bot.mystbin_client.get(
                f"https://mystb.in/{id}")
            lis = ["awesome", "bad", "good"]
            content = get_paste.content
            lencontent = len(content)
            if lencontent > 1080:
                e = discord.Embed(
                    title="I have found this, but the content is to big!",
                    description=f"The content is shown here:  [Link]({get_paste.url})",
                )
                await ctx.send(embed=e)
            else:
                e2 = discord.Embed(
                    title=f"I have found this, is it {choice(lis)}?",
                    description=f"{content}",
                )
                await ctx.send(embed=e2)
        except mystbin.BadPasteID:
            await ctx.send(f"Hmmm.. id : {id} isn't found, try again?")
    
    
    @commands.bot_has_permissions(attach_files=True)
    @commands.command(aliases=["ss"])
    async def screenshot(self, ctx, link: str, wait: int = 3):
        """
        Screenshots a given link.
        If no time is given, it will wait 3 seconds to screenshot
        """

        await ctx.trigger_typing()
        browser = await launch()
        page = await browser.newPage()
        await page.setViewport({"width": 1280, "height": 720})
        try:
            await page.goto(link)
        except pyppeteer.page.PageError:
            await ctx.send("Sorry, I couldn't find anything at that link!")
            await browser.close()
            return
        except Exception:
            await ctx.send(
                "Sorry, I ran into an issue! Make sure to include http:// or https:// at the beginning of the link."
            )
            await browser.close()
            return

        await asyncio.sleep(wait)
        result = await page.screenshot()
        await browser.close()
        f = io.BytesIO(result)
        file = discord.File(f, filename="screenshot.png")
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Random(bot))
