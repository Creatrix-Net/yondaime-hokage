import os
import time
from os.path import join
from pathlib import Path

# import aiozaneapi
import async_cleverbot as ac
import discord
import dotenv
import mystbin
import sentry_sdk
from asyncdagpi import Client
from discord.ext import commands
from discord_slash import SlashCommand
from pretty_help import PrettyHelp

from .botmain.bot.lib import PostStats
from pypresence import Presence
import ast

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True
intents.presences = False



dotenv_file = os.path.join(".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname, 'False').strip('\n')

TOKEN = token_get('TOKEN')
topastoken = token_get('TOPASTOKEN')

sentry_link = token_get('SENTRY')

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = [')', 'm!', 'minato', 'minato ']

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
bot.dagpi = Client(token_get('DAGPI'))
bot.start_time = time.time()

bot.discord_id = token_get('DISCORD_CLIENT_ID')
bot.secrect_client = token_get('DISCORD_CLIENT_SECRET')

bot.statcord = token_get('STATCORD')
bot.auth_pass = token_get('AUTH_PASS')

bot.github = token_get('GITHUB')
bot.owner = token_get('OWNER')
bot.thresholds = (10, 25, 50, 100)
bot.description = "Myself **Minato Namikaze** Aka **Yondaime Hokage** 私の湊波風別名第四火影  ||Music commands may not work as they are in development||"
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('botmain','bot','discord_bot_images')

bot.dblst = token_get('DISCORDBOTLIST')
bot.botlist = token_get('BOTLISTSPACE')
bot.bfd = token_get('BOTSFORDISCORD')
bot.discordboats = token_get('DISCORDBOATS')
bot.discordbotsgg = token_get('DISCORDBOTS')
bot.spacebot = token_get('SPACEBOT')
bot.bladebot = token_get('BLADEBOT')
bot.voidbot = token_get('VOIDBOT')
bot.fateslist = token_get('FATESLIST')

bot.minato_dir = Path(__file__).resolve(strict=True).parent / join('botmain','bot','discord_bot_images')
bot.minato_gif = [f for f in os.listdir(join(bot.minato_dir ,'minato'))]
    
posting = PostStats(bot)

@bot.event
async def on_ready():
    cog_dir = Path(__file__).resolve(strict=True).parent / join('botmain','bot','cogs')
    for filename in os.listdir(cog_dir):
        if os.path.isdir(cog_dir / filename):
            for i in os.listdir(cog_dir / filename):
                if i.endswith('.py'):
                    bot.load_extension(f'botmain.bot.cogs.{filename.strip(" ")}.{i[:-3]}')
        else:
            if filename.endswith('.py'):
                if filename != 'music1.py':
                    bot.load_extension(f'botmain.bot.cogs.{filename[:-3]}')

    current_time = time.time()
    difference = int(round(current_time - bot.start_time))
    stats = bot.get_channel(819128718152695878)
    e = discord.Embed(title=f"Bot Loaded!", description=f"Bot ready by **{time.ctime()}**, loaded all cogs perfectly! Time to load is {difference} secs :)")
    e.set_thumbnail(url=bot.user.avatar_url)
    print('Started The Bot')

    await posting.post_guild_stats_all()
    await stats.send(embed=e)
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name='over Naruto'))


sentry_sdk.init(
    sentry_link,
    traces_sample_rate=1.0
)
try:
    division_by_zero = 1 / 0
except:
    pass

if ast.literal_eval(token_get('LOCAL')):
    try:
        client_id = '779559821162315787'
        RPC = Presence(client_id)
        RPC.connect()
        RPC.update(
            state="火 Minato Namikaze 火", 
            large_image="img_9692",
            small_image="oqy9h2m",
            details ="Konichiwa, myself Minato Namikaze, \n Konohagakure Yondaime Hokage, \n\n I try my best to do every work as a Hokage",
            large_text="Minato Namikaze | 波風ミナト",
            small_text="Minato Namikaze",
            buttons=[{"label": "Invite", "url": "https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&scope=bot%20applications.commands"},
                    {"label": "Website", "url": 'https://dhruvacube.github.io/yondaime-hokage/'}
                    ]
        )
    except: pass

try:
    bot.run(TOKEN)
except RuntimeError:
    bot.logout()
except KeyboardInterrupt:
    bot.logout()

