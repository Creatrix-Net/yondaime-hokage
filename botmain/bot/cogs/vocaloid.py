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
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def rin(self, ctx):
        data = requests.get(url=self.endpoint + 'rin').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def una(self, ctx):
        data = requests.get(url=self.endpoint + 'una').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def gumi(self, ctx):
        data = requests.get(url=self.endpoint + 'gumi').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def ia(self, ctx):
        data = requests.get(url=self.endpoint + 'ia').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def luka(self, ctx):
        data = requests.get(url=self.endpoint + 'luka').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def fukase(self, ctx):
        data = requests.get(url=self.endpoint + 'fukase').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def miku(self, ctx):
        data = requests.get(url=self.endpoint + 'miku').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command(name='len_vocaloid ',aliases=['len'])
    async def _len(self, ctx):
        data = requests.get(url=self.endpoint + 'len').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def kaito(self, ctx):
        data = requests.get(url=self.endpoint + 'kaito').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def teto(self, ctx):
        data = requests.get(url=self.endpoint + 'teto').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def meiko(self, ctx):
        data = requests.get(url=self.endpoint + 'meiko').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def yukari(self, ctx):
        data = requests.get(url=self.endpoint + 'yukari').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def miki(self, ctx):
        data = requests.get(url=self.endpoint + 'miki').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def lily(self, ctx):
        data = requests.get(url=self.endpoint + 'lily').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def mayu(self, ctx):
        data = requests.get(url=self.endpoint + 'mayu').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def aoki(self, ctx):
        data = requests.get(url=self.endpoint + 'aoki').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def zola(self, ctx):
        data = requests.get(url=self.endpoint + 'zola').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

    @commands.command()
    async def diva(self, ctx):
        data = requests.get(url=self.endpoint + 'diva').json()['url']
        e=discord.Embed()
        e.set_image(url=data)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Vocaloid(bot))
