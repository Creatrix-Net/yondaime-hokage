  
import os
import time
from os.path import join
from pathlib import Path
import random

import aiozaneapi
import async_cleverbot as ac
import discord
import dotenv
import mystbin
from asyncdagpi import Client
from discord.ext import commands
from discord.ext.buttons import Paginator

from bot.help import Help


class Page(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass
intents = discord.Intents.all()
intents.members = True
intents.reactions = True
intents.guilds = True

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_file = os.path.join(BASE_DIR,".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname)

TOKEN = token_get('TOKEN')
topastoken = token_get('TOPASTOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or(')'), intents=intents, help_command=Help(),  allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),case_insensitive=True,description="Hi I am **Minato Namikaze**, Yondaime Hokage")
bot.mystbin_client = mystbin.Client()
bot.version = str(token_get('BOT_VER'))
hce = bot.get_command("help")
hce.hidden = True

chatbottoken = token_get('CHATBOTTOKEN')
bot.topken = topastoken #Topgg Token
bot.chatbot = ac.Cleverbot(f"{chatbottoken}")
bot.se = aiozaneapi.Client(token_get('ZANEAPI'))
bot.dagpi = Client(token_get('DAGPI'))
bot.start_time = time.time()

bot.discord_id = token_get('DISCORD_CLIENT_ID')
bot.secrect_client = token_get('DISCORD_CLIENT_SECRET')

bot.sitereq = token_get('REQWEBSITE')

bot.statcord = token_get('STATCORD')

bot.auth_pass = token_get('AUTH_PASS')
bot.lavalink = token_get('LAVALINK')

bot.github = token_get('GITHUB')
bot.owner = token_get('OWNER')
bot.topgg = token_get('TOPGG')
bot.discordbotlist = token_get('DBLST')
bot.thresholds = (10, 25, 50, 100)
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')

minato_dir = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')
minato_gif = [f for f in os.listdir(join(minato_dir ,'minato'))]


# Events
@bot.event
async def on_ready():
    for filename in os.listdir(Path(__file__).resolve(strict=True).parent / join('bot','cogs')):
        if filename.endswith('.py'):
            if filename != 'music.py':
                bot.load_extension(f'bot.cogs.{filename[:-3]}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name='over Naruto'))
    print('My Body is ready!')

#on join send message event
@bot.event
async def on_guild_join(guild):
    img=random.choice(minato_gif)
    file = discord.File(join(minato_dir, 'minato',img), filename=img)
    await guild.system_channel.send(file=file)

    await guild.system_channel.send(f'Hello ** {guild.name}**! I am **{bot.user.mention}**!!! \n> **Help cmd** :\n> ~ **`)help`**\n> or \n> ~ **`{bot.user.mention} help`**')
    await guild.system_channel.send(f'----------\n----------\n**Myself {bot.user.mention} aka Yondaime Hokage**\n----------\n----------\n')
    await guild.system_channel.send(f'> ~ Hey **{guild.owner.mention}** or **anyone with administrator access** please type **`)setup`** in any of the channels in the server to do the setup!')
    await guild.system_channel.send(f'----------')
    '''
    if guild.id not in (568567800910839811 , 632908146305925129):
        await guild.system_channel.send('My **sleeping time** is from')
        await guild.system_channel.send('**00:00 AM IST**  to')
        await guild.system_channel.send('**07:00 AM IST**')
    '''
    
    img=random.choice(minato_gif)
    file = discord.File(join(minato_dir, 'minato',img), filename=img)
    await guild.system_channel.send(file=file)

    e34= discord.Embed(title=f'{guild.name}', color= 0x2ecc71,description='Added')
    if guild.icon:
        e34.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        e34.set_image(url=guild.banner_url_as(format="png"))
    c = bot.get_channel(813954921782706227)
    await c.send(embed=e34)

#when bot leaves the server
@bot.event
async def on_guild_remove(guild):
    e34= discord.Embed(title=f'{guild.name}', color= 0xe74c3c,description='Left')
    if guild.icon:
        e34.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        e34.set_image(url=guild.banner_url_as(format="png"))
    c = bot.get_channel(813954921782706227)
    if guild.name:
        await c.send(embed=e34)

#ban
@bot.event
async def on_member_ban(guild, user):
    bingo = discord.utils.get(guild.categories, name="Bingo Book") if discord.utils.get(guild.categories, name="Bingo Book") else False
    if bingo:
        ban = discord.utils.get(bingo.channels, name="ban") if discord.utils.get(bingo.channels, name="ban") else False
        if ban:
            e=discord.Embed(title='**Ban**',description=f'**{user.mention}** was banned!', color=0xe74c3c)
            e.set_image(url='https://i.imgur.com/B7EAJKM.jpg')
            if user.avatar_url:
                e.set_thumbnail(url=user.avatar_url)
            await ban.send(embed=e)

#unban
@bot.event
async def on_member_unban(guild, user):
    bingo = discord.utils.get(guild.categories, name="Bingo Book") if discord.utils.get(guild.categories, name="Bingo Book") else False
    if bingo:
        unban = discord.utils.get(bingo.channels, name="unban") if discord.utils.get(bingo.channels, name="unban") else False
        if unban:
            e=discord.Embed(title='**Unban**',description=f'**{user.mention}** was unbanned!', color=0x2ecc71)
            e.set_image(url='https://i.imgur.com/O1Xvv7I.jpg')
            if user.avatar_url:
                e.set_thumbnail(url=user.avatar_url)
            await unban.send(embed=e)

#on message event
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message) and message.mention_everyone is False and message.content.lower() == '<@!779559821162315787>' or message.content.lower() == '<@!779559821162315787> prefix':
        await  message.channel.send('The prefix is **)** ,A full list of all commands is available by typing ```)help```')
    if message.channel.id == 814134179049635840:
        embed = message.embeds[0].to_dict()
        
        for guild in bot.guilds:
            try:
                if not guild.id == 747480356625711204: 
                    e = discord.Embed(title=embed['title'],description=embed['description'] , color= 0x2ecc71)
                    e.set_thumbnail(url='https://i.imgur.com/lwGawEv.jpeg')
                    await guild.system_channel.send(embed=e)
            except: print('Tried but failed!')
    await bot.process_commands(message)
                

@bot.event
async def on_command_error(ctx, error):
    guild = ctx.guild
    if isinstance(error, commands.CommandOnCooldown):
        e1 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e1.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e1)
    elif isinstance(error, commands.MissingPermissions):
        e3 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e3.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e3)
    elif isinstance(error, commands.MissingRequiredArgument):
        e4 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e4.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e4)
    '''
    elif isinstance(error, commands.CommandNotFound):
        e2 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e2.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e2)

    elif isinstance(error, commands.CommandInvokeError):
        haha = ctx.author.avatar_url
        e7 = discord.Embed(title="Oh no green you fucked up", description=f"`{error}`")
        e7.add_field(name="Command Caused By?", value=f"{ctx.command}")
        e7.add_field(name="By", value=f"ID : {ctx.author.id}, Name : {ctx.author.name}")
        e7.set_thumbnail(url=f"{haha}")
        e7.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e7)
    else:
        haaha = ctx.author.avatar_url
        e9 = discord.Embed(title="Oh no green you fucked up", description=f"`{error}`")
        e9.add_field(name="Command Caused By?", value=f"{ctx.command}")
        e9.add_field(name="By", value=f"ID : {ctx.author.id}, Name : {ctx.author.name}")
        e9.set_thumbnail(url=f"{haaha}")
        e9.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e9)'''

bot.run(TOKEN)
