import datetime
import random
from os import listdir
from os.path import join
from pathlib import Path

import discord
from discord.ext import commands
from discord.utils import find

TOKEN = 'Nzc5NTU5ODIxMTYyMzE1Nzg3.X7iTqA.PEmxShgoueoJgaE6BvQatCCT4XM'
DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('discord_bot_images')
bot = commands.Bot(command_prefix='.', description="This is a Helper Bot only for the freelance server")

#Commands

#ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

#info
@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"**{ctx.guild.name}**", description=f"{ctx.guild.description if ctx.guild.description else '' }", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="**Server created at**", value=f"{ctx.guild.created_at}")
    embed.add_field(name="**Server Owner**", value=f"<@{ctx.guild.owner_id}>")
    embed.add_field(name="**Server Region**", value=f"{str(ctx.guild.region).upper() if ctx.guild.region else 'No region set till now'}")
    embed.add_field(name="**Server ID**", value=f"{ctx.guild.id}")
    embed.add_field(name="**Members(Bots included)**", value=ctx.guild.member_count)
    embed.set_thumbnail(url=str(ctx.guild.icon_url))
    await ctx.send(embed=embed)

#8ball
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
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'** <@{ctx.author.id}> spanks themselves !!! LOL!**'
    elif member == '@everyone':
        await ctx.send(f'** <@{ctx.author.id}> why would you spank @everyone? **')
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'** <@{ctx.author.id}> spanks {member} !!! Damm! **'
    else:
        desc=f'** <@{ctx.author.id}> spanks themselves !!! LOL! **'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'spank'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'spank',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)


#slap
@bot.command()
async def slap(ctx, member = ''):
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'** <@{ctx.author.id}> slaps themselves !!! LOL!**'
    elif member == '@everyone':
        await ctx.send(f'** <@{ctx.author.id}> why would you slap @everyone? **')
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'** <@{ctx.author.id}> slaps {member} !!! Damm! **'
    else:
        desc=f'** <@{ctx.author.id}> slaps themselves !!! LOL! **'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'slap'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'slap',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)


#hug
@bot.command()
async def hug(ctx, member = ''):
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'** <@{ctx.author.id}> hugs themselves ❤️❤️❤️❤️ **'
    elif member == '@everyone':
        await ctx.send(f'** <@{ctx.author.id}> why would you hug @everyone? **')
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'** <@{ctx.author.id}> hugs {member} !!! ❤️❤️❤️ **'
    else:
        desc=f'** <@{ctx.author.id}> hugs themselves !!! ❤️❤️❤️❤️ **'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'hug'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'hug',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)


#poke
@bot.command()
async def poke(ctx, member = ''):
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'** <@{ctx.author.id}> pokes themselves! **'
    elif member == '@everyone':
        await ctx.send(f'** <@{ctx.author.id}> why would you poke @everyone? **')
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'** {member} <@{ctx.author.id}> pokes you !!! **'
    else:
        desc=f'** <@{ctx.author.id}> hugs themselves !!! **'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'poke'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'poke',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)


#poke
@bot.command()
async def high5(ctx, member = ''):
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'**<@{ctx.author.id}> high-fives **'
    elif member == '@everyone':
        desc=f'**@everyone <@{ctx.author.id}> high-fives **'
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'**<@{ctx.author.id}> high fives {member} !!! **'
    else:
        desc=f'**<@{ctx.author.id}> high-fives **'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'high5'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'high5',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)

#party
@bot.command()
async def party(ctx, member = ''):
    global DEFAULT_GIF_LIST_PATH
    if member == '':
        desc=f'**<@{ctx.author.id}> is partying !!**'
    elif member == '@everyone':
        desc=f'**@everyone <@{ctx.author.id}> is partying!! come join them !! **'
    elif member[:2] == '<@' or member.split('<@')[1].isdigit():
        desc=f'**<@{ctx.author.id}> parties with {member} !!! Yaay !!! **'
    else:
        desc=f'**<@{ctx.author.id}> is partying !!!**'
    onlyfiles = [f for f in listdir(join(DEFAULT_GIF_LIST_PATH ,'party'))]


    embed = discord.Embed(description=desc, timestamp=datetime.datetime.utcnow())
    image_name=random.choice(onlyfiles)

    file = discord.File(join(DEFAULT_GIF_LIST_PATH,'party',image_name), filename=image_name)
    embed.set_image(url=f"attachment://{image_name}")
    await ctx.send(file=file,embed=embed)


#Moderation
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all requirements :rolling_eyes:.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have all the requirements :angry:")

#The below code bans player.
@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f'{member} got banned {"due to "+reason if not reason else ""}')


#The below code unbans player.
@bot.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kick')




# Events
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Naruto", url="https://gogoanime.so/naruto-episode-31"))
    print('My Ready is Body')

#on join send message event
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(f'** Hello {guild.name}! I am Dhruva Shaw bot!!! **')


@bot.listen()
async def on_message(message):
    if message.author.bot or message.author == bot.user:
        return
    if "youtube" in message.content.lower():
        # in this case don't respond with the word "Tutorial" or you will call the on_message event recursively
        await message.channel.send('This is that you want https://www.youtube.com/channel/UCzdpJWTOXXhuSKw-yERbu3g')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if message.author.bot or message.author == bot.user:
        return
    if "fuck" in message.content.lower():
        await message.channel.send(f'Fuck off!!! <@{message.author.id}>')
        await bot.process_commands(message)

@bot.listen()
async def on_message(message):
    if message.author.bot or message.author == bot.user:
        return
    for i in ["hi","hey","hiya","hello","hola","holla"]:
        if i in message.content.lower():
            await message.channel.send(f'**Hello** <@{message.author.id}>')
            await bot.process_commands(message)
            break

bot.run(TOKEN)
