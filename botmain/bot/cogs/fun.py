import datetime
import random
from os import listdir
from os.path import join

import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DEFAULT_GIF_LIST_PATH = bot.DEFAULT_GIF_LIST_PATH
        
    #8ball
    @commands.command(name='8ball')
    async def _8ball(self,ctx, *, question):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful",
            "Stoping asking me fucking studip questions !!!! I need peace bitch!"
        ]
        for i in random.choice(responses).split(' '):
            await ctx.send(f'**{i.upper()}**')

    #spank
    @commands.command()
    async def spank(self,ctx, member = ''):
        if member == '':
            desc=f'** <@{ctx.author.id}> spanks themselves !!! LOL!**'
        elif member == '@everyone':
            await ctx.send(f'** <@{ctx.author.id}> why would you spank @everyone? **')
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'** <@{ctx.author.id}> spanks {member} !!! Damm! **'
        else:
            desc=f'** <@{ctx.author.id}> spanks themselves !!! LOL! **'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'spank'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'spank',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)


    #slap
    @commands.command()
    async def slap(self,ctx, member = ''):
        if member == '':
            desc=f'** <@{ctx.author.id}> slaps themselves !!! LOL!**'
        elif member == '@everyone':
            await ctx.send(f'** <@{ctx.author.id}> why would you slap @everyone? **')
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'** <@{ctx.author.id}> slaps {member} !!! Damm! **'
        else:
            desc=f'** <@{ctx.author.id}> slaps themselves !!! LOL! **'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'slap'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'slap',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)


    #hug
    @commands.command()
    async def hug(self,ctx, member = ''):
        if member == '':
            desc=f'** <@{ctx.author.id}> hugs themselves :heart: :heart: :heart: :heart: **'
        elif member == '@everyone':
            await ctx.send(f'** <@{ctx.author.id}> why would you hug @everyone? **')
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'** <@{ctx.author.id}> hugs {member} !!! :heart: :heart: :heart: **'
        else:
            desc=f'** <@{ctx.author.id}> hugs themselves !!! :heart: :heart: :heart: :heart: **'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'hug'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'hug',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)


    #poke
    @commands.command()
    async def poke(self,ctx, member = ''):
        if member == '':
            desc=f'** <@{ctx.author.id}> pokes themselves! **'
        elif member == '@everyone':
            await ctx.send(f'** <@{ctx.author.id}> why would you poke @everyone? **')
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'** {member} <@{ctx.author.id}> pokes you !!! **'
        else:
            desc=f'** <@{ctx.author.id}> hugs themselves !!! **'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'poke'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'poke',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)


    #poke
    @commands.command()
    async def high5(self,ctx, member = ''):
        if member == '':
            desc=f'**<@{ctx.author.id}> high-fives **'
        elif member == '@everyone':
            desc=f'**@everyone <@{ctx.author.id}> high-fives **'
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'**<@{ctx.author.id}> high fives {member} !!! **'
        else:
            desc=f'**<@{ctx.author.id}> high-fives **'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'high5'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'high5',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)

    #party
    @commands.command()
    async def party(self,ctx, member = ''):
        if member == '':
            desc=f'**<@{ctx.author.id}> is partying !!**'
        elif member == '@everyone':
            desc=f'**@everyone <@{ctx.author.id}> is partying!! come join them !! **'
        elif member[:2] == '<@' or member.split('<@')[1].isdigit():
            desc=f'**<@{ctx.author.id}> parties with {member} !!! Yaay !!! **'
        else:
            desc=f'**<@{ctx.author.id}> is partying !!!**'
        onlyfiles = [f for f in listdir(join(self.DEFAULT_GIF_LIST_PATH ,'party'))]


        embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
        image_name=random.choice(onlyfiles)

        file = discord.File(join(self.DEFAULT_GIF_LIST_PATH,'party',image_name), filename=image_name)
        embed.set_image(url=f"attachment://{image_name}")
        await ctx.send(file=file,embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
