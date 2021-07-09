import os
import time
from os.path import join
from pathlib import Path

import discord
import dotenv
import sentry_sdk
from discord.ext import commands
from discord_slash import SlashCommand
from pathlib import Path
from discord_components import DiscordComponents

from pypresence import Presence
import ast
import DiscordUtils


from botmain.bot.lib import MenuHelp, HelpClassPretty

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True
intents.presences = False
intents.integrations = True


dotenv_file = os.path.join(Path(__file__).resolve().parent.parent / ".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname, 'False').strip('\n')

TOKEN = token_get('TOKEN')
sentry_link = token_get('SENTRY')

def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    prefixes = [')', 'm!', 'minato', 'minato ']

    if not message.guild:
        return 'm!'

    return commands.when_mentioned_or(*prefixes)(bot, message)

bot = commands.AutoShardedBot(
    command_prefix = get_prefix,
    intents = intents, 
    help_command = HelpClassPretty(
        show_index=True,
        menu = MenuHelp(
            page_left=":pikawalk:852872040016248863", 
            page_right=":thiccguy:852872039874428939", 
            remove=":sus:852797247304761405",
            active_time=60.0
        )
    ),  
    allowed_mentions = discord.AllowedMentions(
        users=True, 
        roles=False, 
        everyone=False
    ),
    case_insensitive=True,
    description="Hi I am **Minato Namikaze**, Yondaime Hokage",
    owner_id=571889108046184449
)
slash = SlashCommand(bot, sync_commands=True)

bot.version = str(token_get('BOT_VER'))

bot.start_time = time.time()
bot.github = token_get('GITHUB')
bot.owner = token_get('OWNER')
bot.description = "Myself **Minato Namikaze** Aka **Yondaime Hokage** 私の湊波風別名第四火影"
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('botmain','bot','discord_bot_images')


bot.minato_dir = Path(__file__).resolve(strict=True).parent / join('botmain','bot','discord_bot_images')
bot.minato_gif = [f for f in os.listdir(join(bot.minato_dir ,'minato'))]


@bot.event
async def on_ready():
    DiscordComponents(bot)
    cog_dir = Path(__file__).resolve(strict=True).parent / join('botmain','bot','cogs')
    for filename in os.listdir(cog_dir):
        if os.path.isdir(cog_dir / filename):
            for i in os.listdir(cog_dir / filename):
                if i.endswith('.py'):
                    bot.load_extension(f'botmain.bot.cogs.{filename.strip(" ")}.{i[:-3]}')
        else:
            if filename.endswith('.py'):
                bot.load_extension(f'botmain.bot.cogs.{filename[:-3]}')
    current_time = time.time()
    difference = int(round(current_time - bot.start_time))
    stats = bot.get_channel(819128718152695878)
    e = discord.Embed(title=f"Bot Loaded!", description=f"Bot ready by **{time.ctime()}**, loaded all cogs perfectly! Time to load is {difference} secs :)",color=discord.Colour.random())
    e.set_thumbnail(url=bot.user.avatar_url)
    print('Started The Bot')
    
    try:
        await stats.send(embed=e)
    except:
        pass
    await bot.change_presence(
        status=discord.Status.idle, 
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name='over Naruto'
        )
    )


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
            large_image="fzglchm",
            small_image="m57xri9",
            details ="Konichiwa, myself Minato Namikaze, \n Konohagakure Yondaime Hokage, \n\n I try my best to do every work as a Hokage",
            large_text="Minato Namikaze | 波風ミナト",
            small_text="Minato Namikaze",
            buttons=[{"label": "Invite", "url": "https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&scope=bot%20applications.commands"},
                    {"label": "Website", "url": 'https://dhruvacube.github.io/yondaime-hokage/'}
                    ]
        )
    except: pass

if __name__ == '__main__':
    bot.run(TOKEN)

