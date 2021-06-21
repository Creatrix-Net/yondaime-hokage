from discord.ext import commands
from discord_slash import SlashContext, cog_ext

from ...lib import meek_api as meek_moe

class VocaloidSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Get some kawai pictures of the vocaloids.'

    @cog_ext.cog_slash(name="rin", description='Rin kawai picture')
    async def rin(self, ctx: SlashContext):
        '''Rin kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('rin'))

    @cog_ext.cog_slash(name="una", description='Una kawai picture')
    async def una(self, ctx: SlashContext):
        '''Una kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('una'))

    @cog_ext.cog_slash(name="gumi", description='Gumi kawai picture')
    async def gumi(self, ctx: SlashContext):
        '''Gumi kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('gumi'))

    @cog_ext.cog_slash(name="ia", description='Ia kawai picture')
    async def ia(self, ctx: SlashContext):
        '''Ia kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('ia'))

    @cog_ext.cog_slash(name="luka", description='Luka kawai picture')
    async def luka(self, ctx: SlashContext):
        '''Luka kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('luka'))

    @cog_ext.cog_slash(name="fukase", description='Fukase kawai picture')
    async def fukase(self, ctx: SlashContext):
        '''Fukase kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('fukase'))

    @cog_ext.cog_slash(name="miku", description='Hatsune Miku kawai picture')
    async def miku(self, ctx: SlashContext):
        '''Hatsune Miku kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('miku'))

    @cog_ext.cog_slash(name="len", description='Len kawai picture')
    async def _len(self, ctx: SlashContext):
        '''Len kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('len'))

    @cog_ext.cog_slash(name="kaito", description='Kaito kawai picture')
    async def kaito(self, ctx: SlashContext):
        '''Kaito kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('kaito'))

    @cog_ext.cog_slash(name="teto", description='Teto kawai picture')
    async def teto(self, ctx: SlashContext):
        '''Teto kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('teto'))

    @cog_ext.cog_slash(name="meiko", description='Meiko kawai picture')
    async def meiko(self, ctx: SlashContext):
        '''Meiko kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('meiko'))

    @cog_ext.cog_slash(name="yukari", description='Yukari kawai picture')
    async def yukari(self, ctx: SlashContext):
        '''Yukari kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('yukari'))

    @cog_ext.cog_slash(name="miki", description='Miki kawai picture')
    async def miki(self, ctx: SlashContext):
        '''Miki kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('miki'))

    @cog_ext.cog_slash(name="lily", description='Lily kawai picture')
    async def lily(self, ctx: SlashContext):
        '''Lily kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('lily'))

    @cog_ext.cog_slash(name="mayu", description='Mayu kawai picture')
    async def mayu(self, ctx: SlashContext):
        '''Mayu kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('mayu'))

    @cog_ext.cog_slash(name="aoki", description='Aoki kawai picture')
    async def aoki(self, ctx: SlashContext):
        '''Aoki kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('aoki'))

    @cog_ext.cog_slash(name="zola", description='Zola kawai picture')
    async def zola(self, ctx: SlashContext):
        '''Zola kawai picture'''
        await ctx.send(embed=await meek_moe.meek_api('zola'))

    @cog_ext.cog_slash(name="diva", description='Random picturs from Project Diva')
    async def diva(self, ctx: SlashContext):
        '''Random picturs from Project Diva'''
        await ctx.send(embed=await meek_moe.meek_api('diva'))


def setup(bot):
    bot.add_cog(VocaloidSlash(bot))
