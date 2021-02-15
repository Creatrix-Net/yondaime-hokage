import discord
from discord.ext import commands
from random import choice 
import django
import os

  

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '....bot.settings')
django.setup()

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github
    
    @commands.command()
    async def naruto(self, ctx):
        anime_category = AnimeName.objects.filter(anime_name__in=['Naruto','Shippuden', 'Naruto Shippuden', 'Boruto']).all()
        await ctx.send(choice(AnimeImage.objects.filter(anime_category=choice(anime_category).iterator())))
