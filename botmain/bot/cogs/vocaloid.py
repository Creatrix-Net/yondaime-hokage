import discord
from discord.ext import commands
import requests 

class Vocaloid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endpoint = 'https://api.meek.moe/'

    @commands.command()
    async def rin(self, ctx):
        data = requests.get(url=self.endpoint + 'rin').json()['url']
        await ctx.send(data)

    @commands.command()
    async def rin(self, ctx):
        data = requests.get(url=self.endpoint + 'rin').json()['url']
        await ctx.send(data)

    @commands.command()
    async def una(self, ctx):
        data = requests.get(url=self.endpoint + 'una').json()['url']
        await ctx.send(data)

    @commands.command()
    async def gumi(self, ctx):
        data = requests.get(url=self.endpoint + 'gumi').json()['url']
        await ctx.send(data)

    @commands.command()
    async def ia(self, ctx):
        data = requests.get(url=self.endpoint + 'ia').json()['url']
        await ctx.send(data)

    @commands.command()
    async def luka(self, ctx):
        data = requests.get(url=self.endpoint + 'luka').json()['url']
        await ctx.send(data)

    @commands.command()
    async def fukase(self, ctx):
        data = requests.get(url=self.endpoint + 'fukase').json()['url']
        await ctx.send(data)

    @commands.command()
    async def miku(self, ctx):
        data = requests.get(url=self.endpoint + 'miku').json()['url']
        await ctx.send(data)

    @commands.command(aliases=['len'])
    async def _len(self, ctx):
        data = requests.get(url=self.endpoint + 'len').json()['url']
        await ctx.send(data)

    @commands.command()
    async def kaito(self, ctx):
        data = requests.get(url=self.endpoint + 'kaito').json()['url']
        await ctx.send(data)

    @commands.command()
    async def teto(self, ctx):
        data = requests.get(url=self.endpoint + 'teto').json()['url']
        await ctx.send(data)

    @commands.command()
    async def meiko(self, ctx):
        data = requests.get(url=self.endpoint + 'meiko').json()['url']
        await ctx.send(data)

    @commands.command()
    async def yukari(self, ctx):
        data = requests.get(url=self.endpoint + 'yukari').json()['url']
        await ctx.send(data)

    @commands.command()
    async def miki(self, ctx):
        data = requests.get(url=self.endpoint + 'miki').json()['url']
        await ctx.send(data)

    @commands.command()
    async def lily(self, ctx):
        data = requests.get(url=self.endpoint + 'lily').json()['url']
        await ctx.send(data)

    @commands.command()
    async def mayu(self, ctx):
        data = requests.get(url=self.endpoint + 'mayu').json()['url']
        await ctx.send(data)

    @commands.command()
    async def aoki(self, ctx):
        data = requests.get(url=self.endpoint + 'aoki').json()['url']
        await ctx.send(data)

    @commands.command()
    async def zola(self, ctx):
        data = requests.get(url=self.endpoint + 'zola').json()['url']
        await ctx.send(data)

def setup(bot):
    bot.add_cog(Vocaloid(bot))
