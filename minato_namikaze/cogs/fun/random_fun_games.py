from __future__ import annotations

import asyncio
import io
import logging
import os
from random import choice
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import discord
import mystbin
from discord.ext import commands
from discord.ext import owoify
from gtts import gTTS
from PIL import Image

from minato_namikaze.lib import Embed
from minato_namikaze.lib import LinksAndVars
from minato_namikaze.lib import MemberID

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib import Context

    from ... import MinatoNamikazeBot


class Random(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.mystbin_client = mystbin.Client()
        self.description = "Some random fun and usefull commands."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{GAME DIE}")

    @commands.command()
    @commands.cooldown(1, 40, commands.BucketType.guild)
    async def braille(self, ctx: Context, user: discord.Member = None):
        user = user or ctx.author
        file = await self.bot.se.braille(f"{user.avatar_url}")
        await ctx.send(file)

    @braille.error
    async def braille_handler(self, ctx: Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            l = self.bot.get_command("braille")
            left = l.get_cooldown_retry_after(ctx)
            msg = await ctx.send("Just Getting The Cooldown")
            e = discord.Embed(
                title=f"Cooldown left - {round(left)}",
                color=discord.colour.Color.from_rgb(231, 84, 128),
            )
            await msg.edit(content="", embed=e)

    @commands.command(aliases=["takeitback"], usage="<member.mention>")
    async def insult(
        self,
        ctx: Context,
        user: MemberID | discord.Member | None = None,
    ):
        """
        Insult a user
        `user` the user you would like to insult
        """
        if user:
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
                    embed=Embed(
                        title=":warning:",
                        description=choice(LinksAndVars.insults.value),
                    ),
                )
        else:
            await ctx.send(
                ctx.message.author.mention,
                embed=Embed(
                    title=":warning:",
                    description=choice(LinksAndVars.insults.value),
                ),
            )

    @commands.command(usage="{text}")
    async def owoify(self, ctx: Context, text: str):
        """Owoify the message"""
        lol = owoify.owoify(f"{text}")
        await ctx.send(lol)

    @commands.command()
    @commands.cooldown(1, 40, commands.BucketType.guild)
    async def qr(self, ctx: Context, colour="255-255-255", *, url: str | None = None):
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
            if colour not in col:
                if url is None:
                    url = ""
                colour = f"{colour} {url}"
                colour1 = colour.replace(" ", "+")
                qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={colour1}"
                e.set_image(url=qr)
                await msg.edit(content="", embed=e)
            else:
                pass

    @commands.command(usage="<name>")
    async def sn(self, ctx: Context, *, name: str):
        """Introduce yourself to everyone"""
        tts = gTTS(text=f"Hi! {name} is really cool!", lang="en")
        tts.save("announce.mp3")
        await ctx.send(file=discord.File("announce.mp3"))
        await asyncio.sleep(5)
        os.remove("announce.mp3")

    @commands.command(usage="<text>")
    async def tts(self, ctx: Context, *, text: str):
        """Generate text to speech messages"""
        lol = gTTS(text=text)
        lol.save("tts.mp3")
        await ctx.send(file=discord.File("tts.mp3"))
        await asyncio.sleep(5)
        os.remove("tts.mp3")

    @commands.command(
        aliases=["color", "colour", "sc"],
        usage="<hexadecimal colour code>",
    )
    async def show_color(self, ctx: Context, *, color: discord.Colour):
        """Enter a color and you will see it!"""
        file = io.BytesIO()
        Image.new("RGB", (200, 90), color.to_rgb()).save(file, format="PNG")
        file.seek(0)
        em = Embed(color=color, title=f"Showing Color: {str(color)}")
        em.set_image(url="attachment://color.png")
        await ctx.send(file=discord.File(file, "color.png"), embed=em)

    @commands.command(aliases=["myst"], usage="<text>")
    async def mystbin(self, ctx: Context, *, text: str):
        """Generate an Mystbin for yourself"""
        paste = await self.mystbin_client.post(f"{text}", syntax="python")
        e = discord.Embed(
            title="I have created a mystbin link for you!",
            description=f"[Click Here]({paste.url})",
        )
        await ctx.send(embed=e)

    @commands.command(aliases=["getmyst"], usage="<mystbin_id>")
    async def getmystbin(self, ctx: Context, id: str):
        """Get your Mystbi using your id"""
        try:
            get_paste = await self.mystbin_client.get(f"https://mystb.in/{id}")
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

    #     await ctx.trigger_typing()
    #     browser = await launch()
    #     page = await browser.newPage()
    #     await page.setViewport({"width": 1280, "height": 720})
    #     try:
    #         await page.goto(link)
    #     except pyppeteer.page.PageError:
    #         await ctx.send("Sorry, I couldn't find anything at that link!")
    #         await browser.close()
    #         return
    #     except Exception:
    #         await ctx.send(
    #             "Sorry, I ran into an issue! Make sure to include https:// or https:// at the beginning of the link."
    #         )
    #         await browser.close()
    #         return

    #     await asyncio.sleep(wait)
    #     result = await page.screenshot()
    #     await browser.close()
    #     f = io.BytesIO(result)
    #     file = discord.File(f, filename="screenshot.png")
    #     await ctx.send(file=file)


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Random(bot))
