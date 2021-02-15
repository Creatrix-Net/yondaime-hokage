import discord
from discord.ext import commands
import requests 

class Vocaloid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.endpoint = 'https://api.meek.moe/'

    @commands.command()
    async def rin(self, ctx):
        data = requests.get(url=self.endpoint + rin).json()['url']
        await ctx.guild.send(data)
