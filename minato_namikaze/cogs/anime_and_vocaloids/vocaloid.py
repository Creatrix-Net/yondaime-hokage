from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from lib.functions import meek_api

if TYPE_CHECKING:
    from ... import MinatoNamikazeBot

class Vocaloid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Get some kawai pictures of the vocaloids."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="miku_wave", id=940993740967931914)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def rin(self, ctx: commands.Context):
        """Rin kawai picture"""
        await ctx.send(embed=await meek_api("rin"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def una(self, ctx: commands.Context):
        """Una kawai picture"""
        await ctx.send(embed=await meek_api("una"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def gumi(self, ctx: commands.Context):
        """Gumi kawai picture"""
        await ctx.send(embed=await meek_api("gumi"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ia(self, ctx: commands.Context):
        """Ia kawai picture"""
        await ctx.send(embed=await meek_api("ia"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def luka(self, ctx: commands.Context):
        """Luka kawai picture"""
        await ctx.send(embed=await meek_api("luka"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def fukase(self, ctx: commands.Context):
        """Fukase kawai picture"""
        await ctx.send(embed=await meek_api("fukase"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def miku(self, ctx: commands.Context):
        """Hatsune Miku kawai picture"""
        await ctx.send(embed=await meek_api("miku"))

    @commands.command(name="len")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def _len(self, ctx: commands.Context):
        """Len kawai picture"""
        await ctx.send(embed=await meek_api("len"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def kaito(self, ctx: commands.Context):
        """Kaito kawai picture"""
        await ctx.send(embed=await meek_api("kaito"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def teto(self, ctx: commands.Context):
        """Teto kawai picture"""
        await ctx.send(embed=await meek_api("teto"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def meiko(self, ctx: commands.Context):
        """Meiko kawai picture"""
        await ctx.send(embed=await meek_api("meiko"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def yukari(self, ctx: commands.Context):
        """Yukari kawai picture"""
        await ctx.send(embed=await meek_api("yukari"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def miki(self, ctx: commands.Context):
        """Miki kawai picture"""
        await ctx.send(embed=await meek_api("miki"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def lily(self, ctx: commands.Context):
        """Lily kawai picture"""
        await ctx.send(embed=await meek_api("lily"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def mayu(self, ctx: commands.Context):
        """Mayu kawai picture"""
        await ctx.send(embed=await meek_api("mayu"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def aoki(self, ctx: commands.Context):
        """Aoki kawai picture"""
        await ctx.send(embed=await meek_api("aoki"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def zola(self, ctx: commands.Context):
        """Zola kawai picture"""
        await ctx.send(embed=await meek_api("zola"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def diva(self, ctx: commands.Context):
        """Random picturs from Project Diva"""
        await ctx.send(embed=await meek_api("diva"))


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Vocaloid(bot))
