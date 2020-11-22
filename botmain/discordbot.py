import datetime
import random
import re
from os import listdir
from os.path import isfile, join
from pathlib import Path
from urllib import parse, request

import discord
from discord.ext import commands

BASE_DIR = Path(__file__).resolve().parent.parent
TOKEN = 'Nzc5NTU5ODIxMTYyMzE1Nzg3.X7iTqA.PEmxShgoueoJgaE6BvQatCCT4XM'
bot = commands.Bot(command_prefix='.', description="This is a Helper Bot only for the freelance server")

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    await ctx.send(numOne + numTwo)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description=f"{ctx.guild.description if ctx.guild.description else '' }", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"<@{ctx.guild.owner_id}>")
    embed.add_field(name="Server Region", value=f"{str(ctx.guild.region).upper() if ctx.guild.region else 'No region set till now'}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    embed.add_field(name="Members(Bots included)", value=ctx.guild.member_count)
    embed.set_thumbnail(url=str(ctx.guild.icon_url))
    await ctx.send(embed=embed)

@bot.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
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
@bot.command()
async def spank(ctx, member = ''):
    if member == '':
        desc=f'<@{ctx.author.id}> spanks itself!!! LOL!'
    elif member[:2] == '<@':
        desc=f'<@{ctx.author.id}> spanks {member} !!! Damm!'
    else:
        desc=f'<@{ctx.author.id}> spanks itself!!! LOL!'
    onlyfiles = [f for f in listdir(join(BASE_DIR,'botmain','discord_bot_images','spank'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(BASE_DIR,'botmain','discord_bot_images','spank',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)

# Events
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Naruto", url="https://gogoanime.so/naruto-episode-31"))
    print('My Ready is Body')


@bot.listen()
async def on_message(message):
    if "tutorial" in message.content.lower():
        # in this case don't respond with the word "Tutorial" or you will call the on_message event recursively
        await message.channel.send('This is that you want https://www.youtube.com/channel/UCzdpJWTOXXhuSKw-yERbu3g')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if "fuck" in message.content.lower():
        await message.channel.send(f'Fuck off!!! <@{message.author.id}>')
        await bot.process_commands(message)

bot.run(TOKEN)
