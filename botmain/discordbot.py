import os
import time
from os.path import join
from pathlib import Path
from discord_slash import SlashCommand


import aiozaneapi
import async_cleverbot as ac
import discord
import dotenv
import mystbin
from asyncdagpi import Client
from discord.ext import commands
from discord.ext.buttons import Paginator
from pretty_help import PrettyHelp
import DiscordUtils


# from .bot.help import Help


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

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = [')', 'm!', 'm']

    if not message.guild:
        return 'm!'

    return commands.when_mentioned_or(*prefixes)(bot, message)

bot = commands.Bot(command_prefix=get_prefix,intents=intents, help_command=PrettyHelp(show_index=True),  allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),case_insensitive=True,description="Hi I am **Minato Namikaze**, Yondaime Hokage")
slash = SlashCommand(bot, sync_commands=True)

bot.mystbin_client = mystbin.Client()
bot.version = str(token_get('BOT_VER'))
hce = bot.get_command("help")

chatbottoken = token_get('CHATBOTTOKEN')
bot.topken = topastoken #Topgg Token
bot.chatbot = ac.Cleverbot(f"{chatbottoken}")
bot.se = aiozaneapi.Client(token_get('ZANEAPI'))
bot.dagpi = Client(token_get('DAGPI'))
bot.start_time = time.time()

bot.discord_id = token_get('DISCORD_CLIENT_ID')
bot.secrect_client = token_get('DISCORD_CLIENT_SECRET')

bot.statcord = token_get('STATCORD')
bot.auth_pass = token_get('AUTH_PASS')

bot.github = token_get('GITHUB')
bot.owner = token_get('OWNER')
bot.discordbotlist = token_get('DBLST')
bot.thresholds = (10, 25, 50, 100)
bot.description = "Myself **Minato Namikaze** Aka **Yondaime Hokage** 私の湊波風別名第四火影 "
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')

bot.topgg = token_get('TOPGG')
bot.dblst = token_get('DISCORDBOTLIST')
bot.botlist = token_get('BOTLISTSPACE')
bot.bfd = token_get('BOTSFORDISCORD')
bot.discordboats = token_get('DISCORDBOATS')
bot.discordbotsgg = token_get('DISCORDBOTS')
bot.spacebot = token_get('SPACEBOT')

bot.minato_dir = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')
bot.minato_gif = [f for f in os.listdir(join(bot.minato_dir ,'minato'))]
    
music = DiscordUtils.Music()

# Events
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name='over Naruto'))
    cog_dir = Path(__file__).resolve(strict=True).parent / join('bot','cogs')
    for filename in os.listdir(cog_dir):
        if os.path.isdir(cog_dir / filename):
            for i in os.listdir(cog_dir / filename):
                if i.endswith('.py'):
                    bot.load_extension(f'bot.cogs.{filename.strip(" ")}.{i[:-3]}')
        else:
            if filename.endswith('.py'):
                if filename != 'music1.py':
                    bot.load_extension(f'bot.cogs.{filename[:-3]}')

    current_time = time.time()
    difference = int(round(current_time - bot.start_time))
    stats = bot.get_channel(819128718152695878)
    e = discord.Embed(title=f"Bot Loaded!", description=f"Bot ready by **{time.ctime()}**, loaded all cogs perfectly! Time to load is {difference} secs :)")
    e.set_thumbnail(url=bot.user.avatar_url)
    print('Started The Bot')

    await stats.send(embed=e)    

@bot.event
async def on_command_error(ctx, error):
    guild = ctx.guild
    if isinstance(error, commands.CommandOnCooldown):
        e1 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e1.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e1, delete_after=3)
    elif isinstance(error, commands.MissingPermissions):
        e3 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e3.set_footer(text=f"{ctx.author.name}")
        await ctx.send(embed=e3, delete_after=3)
    elif isinstance(error, commands.MissingRequiredArgument):
        e4 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e4.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e4, delete_after=2)
    elif isinstance(error, commands.CommandNotFound):
        e2 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e2.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e2, delete_after=3)

    elif isinstance(error, commands.CommandInvokeError):
        perms= 8 #1073737719 #2147483656
        e7 = discord.Embed(title="Oh no, I guess I have not been given proper access! Or some internal error", description=f"`{error}`")
        e7.add_field(name="Command Error Caused By:", value=f"{ctx.command}")
        e7.add_field(name="By", value=f"{ctx.author.name}")
        e7.add_field(name="MY INVITE LINK", value=f"[LINK](https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions={perms}&scope=bot)")
        e7.set_thumbnail(url=f"https://i.imgur.com/1zey3je.jpg")
        e7.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e7)
  
    else:
        haaha = ctx.author.avatar_url
        e9 = discord.Embed(title="Oh no there was some error", description=f"`{error}`")
        e9.add_field(name="**Command Error Caused By**", value=f"{ctx.command}")
        e9.add_field(name="**By**", value=f"**ID** : {ctx.author.id}, **Name** : {ctx.author.name}")
        e9.set_thumbnail(url=f"{haaha}")
        e9.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e9)



bot.run(TOKEN)
