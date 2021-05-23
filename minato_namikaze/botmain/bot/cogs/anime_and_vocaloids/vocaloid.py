import discord
import requests
from discord.ext import commands


class Vocaloid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endpoint = 'https://api.meek.moe/'
        self.description = 'Get some kawai pictures of the vocaloids.'
    
    async def meek_api(self,ctx, name):
        data = requests.get(url = self.endpoint + name).json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        return e

    @commands.command()
    async def rin(self, ctx):
        '''Rin kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'rin'))

    @commands.command()
    async def una(self, ctx):
        '''Una kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'una'))

    @commands.command()
    async def gumi(self, ctx):
        '''Gumi kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'gumi'))

    @commands.command()
    async def ia(self, ctx):
        '''Ia kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'ia'))

    @commands.command()
    async def luka(self, ctx):
        '''Luka kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'luka'))

    @commands.command()
    async def fukase(self, ctx):
        '''Fukase kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'fukase'))

    @commands.command()
    async def miku(self, ctx):
        '''Hatsune Miku kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'miku'))

    @commands.command(name='len')
    async def _len(self, ctx):
        '''Len kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'len'))

    @commands.command()
    async def kaito(self, ctx):
        '''Kaito kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'kaito'))

    @commands.command()
    async def teto(self, ctx):
        '''Teto kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'teto'))

    @commands.command()
    async def meiko(self, ctx):
        '''Meiko kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'meiko'))

    @commands.command()
    async def yukari(self, ctx):
        '''Yukari'''
        await ctx.send(embed = await self.meek_api(ctx,'yukari'))

    @commands.command()
    async def miki(self, ctx):
        '''Miki kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'miki'))

    @commands.command()
    async def lily(self, ctx):
        '''Lily kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'lily'))

    @commands.command()
    async def mayu(self, ctx):
        '''Mayu kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'mayu'))

    @commands.command()
    async def aoki(self, ctx):
        '''Aoki kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'aoki'))

    @commands.command()
    async def zola(self, ctx):
        '''Zola kawai picture'''
        await ctx.send(embed = await self.meek_api(ctx,'zola'))

    @commands.command()
    async def diva(self, ctx):
        '''Random picturs from Project Diva'''
        await ctx.send(embed = await self.meek_api(ctx,'diva'))

def setup(bot):
    bot.add_cog(Vocaloid(bot))
