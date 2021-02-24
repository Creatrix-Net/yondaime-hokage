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
dotenv_file = os.path.join(BASE_DIR, "botmain",".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname)

TOKEN = token_get('TOKEN')
topastoken = token_get('TOPASTOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or(')'), intents=intents, help_command=Help(),  allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),case_insensitive=True,description="Hi I am **Minato Namikaze**, Yondaime Hokage")
bot.mystbin_client = mystbin.Client()
bot.version = "1"
hce = bot.get_command("help")
hce.hidden = True
chatbottoken = token_get('CHATBOTTOKEN')
bot.topken = topastoken #Topgg Token
bot.chatbot = ac.Cleverbot(f"{chatbottoken}")
bot.se = aiozaneapi.Client(token_get('ZANEAPI'))
bot.dagpi = Client(token_get('DAGPI'))
bot.start_time = time.time()
bot.github = token_get('GITHUB')
bot.owner = token_get('OWNER')
bot.topgg = token_get('TOPGG')
bot.thresholds = (10, 25, 50, 100)
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')

minato_dir = Path(__file__).resolve(strict=True).parent
minato_gif = onlyfiles = [f for f in os.listdir(join(minato_dir ,'minato'))]

# Events
@bot.event
async def on_ready():
    for filename in os.listdir(Path(__file__).resolve(strict=True).parent / join('bot','cogs')):
        if filename.endswith('.py'):
            bot.load_extension(f'bot.cogs.{filename[:-3]}')
    await bot.change_presence(activity=discord.Streaming(name="Naruto", url=token_get("WEBSITE")))
    print('My Body is ready!')

#on join send message event
@bot.event
async def on_guild_join(guild):
    hokage_roles = discord.utils.get(guild.roles, name="Hokage") if discord.utils.get(guild.roles, name="Hokage") else False
    hokage = hokage_roles if hokage_roles else await guild.create_role(name="Hokage",mentionable=True,hoist=True,colour=discord.Colour.dark_orange())
    img=random.choice(minato_gif)
    file = discord.File(join(minato_dir, 'minato',img), filename=img)
    await guild.system_channel.send(file=file)

    await guild.system_channel.send(f'Hello ** {guild.name}**! I am **{bot.user.mention}**!!! do type **) help** or **{bot.user.mention} help** for commands!')
    await guild.system_channel.send(f'Myself {bot.user.mention} aka Yandaime Hokage')
    await guild.system_channel.send(f'Hey @here, **{guild.owner}** or **anyone with administrator access** please type **)setup** in any of the channels in the server to do the setup!')
    
    img=random.choice(minato_gif)
    file = discord.File(join(minato_dir, 'minato',img), filename=img)
    await guild.system_channel.send(file=file)

    e34= discord.Embed(title=f'{guild.name}', color='green')
    if ctx.guild.icon:
        e34.set_thumbnail(url=guild.icon_url)
    if ctx.guild.banner:
        e34.set_image(url=guild.banner_url_as(format="png"))


@bot.event
async def on_command_error(ctx, error):
    guild = ctx.guild
    if isinstance(error, commands.CommandOnCooldown):
        e1 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e1.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e1)
    elif isinstance(error, commands.CommandNotFound):
        e2 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e2.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e2)
    elif isinstance(error, commands.MissingPermissions):
        e3 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e3.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e3)
    elif isinstance(error, commands.MissingRequiredArgument):
        e4 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e4.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e4)
    '''elif isinstance(error, commands.CommandInvokeError):
        haha = ctx.author.avatar_url
        e7 = discord.Embed(title="Oh no green you fucked up", description=f"`{error}`")
        e7.add_field(name="Command Caused By?", value=f"{ctx.command}")
        e7.add_field(name="By?", value=f"ID : {ctx.author.id}, Name : {ctx.author.name}")
        e7.set_thumbnail(url=f"{haha}")
        e7.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e7)
    else:
        haaha = ctx.author.avatar_url
        e9 = discord.Embed(title="Oh no green you fucked up", description=f"`{error}`")
        e9.add_field(name="Command Caused By?", value=f"{ctx.command}")
        e9.add_field(name="By?", value=f"ID : {ctx.author.id}, Name : {ctx.author.name}")
        e9.set_thumbnail(url=f"{haaha}")
        e9.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e9)'''

bot.run(TOKEN)
