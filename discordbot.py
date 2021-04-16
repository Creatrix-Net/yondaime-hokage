import os
import time
from os.path import join
from pathlib import Path
from discord_slash import SlashCommand
import sentry_sdk


import aiozaneapi
import async_cleverbot as ac
import discord
import dotenv
import mystbin
from asyncdagpi import Client
from discord.ext import commands, ipc
from discord.ext.buttons import Paginator
from pretty_help import PrettyHelp
import DiscordUtils


from botmain.bot.lib.util.post_user_stats import PostStats


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


dotenv_file = os.path.join(".env")
def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname)

TOKEN = token_get('TOKEN')
topastoken = token_get('TOPASTOKEN')

sentry_link = token_get('SENTRY')

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
bot.voidbot = token_get('FATESLIST')
bot.fateslist = token_get('VOIDBOT')

bot.minato_dir = Path(__file__).resolve(strict=True).parent / join('botmain','bot','discord_bot_images')
bot.minato_gif = [f for f in os.listdir(join(bot.minato_dir ,'minato'))]
    
music = DiscordUtils.Music()
posting = PostStats(bot)

ipc1 = ipc.Server(bot, host='localhost',secret_key=token_get('AUTH_PASS'))

# Events
import threading

@bot.event
async def on_ready():
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bot.settings')

    # threading.Thread(target=os.system('python manage.py runserver')).start()
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name='over Naruto'))
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
    # from django.conf import settings
    # settings.BOT = bot

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
        c = bot.get_channel(830366314761420821)
        
        e7 = discord.Embed(title="Oh no, I guess I have not been given proper access! Or some internal error", description=f"`{error}`")
        e7.add_field(name="Command Error Caused By:", value=f"{ctx.command}")
        e7.add_field(name="By", value=f"{ctx.author.name}")
        e7.add_field(name="MY INVITE LINK", value=f'[LINK](https://discord.com/oauth2/authorize?client_id={bot.discord_id}&permissions=8&scope=bot%20applications.commands)')
        e7.set_thumbnail(url=f"https://i.imgur.com/1zey3je.jpg")
        e7.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e7, delete_after=2)
        await c.send(embed=e7)
        

        await ctx.send('**Sending the error report info to my developer**', delete_after=2)
        e = discord.Embed(title=f'In **{ctx.guild.name}**',description=f'User affected {ctx.message.author}' , color= 0x2ecc71)
        if ctx.guild.icon:
            e.set_thumbnail(url=ctx.guild.icon_url)
        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner_url_as(format="png"))
        e.add_field(name='**Total Members**',value=ctx.guild.member_count)
        e.add_field(name='**Bots**',value=sum(1 for member in ctx.guild.members if member.bot))
        e.add_field(name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True)
        e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
        await ctx.send('**Error report was successfully sent**', delete_after=2)
        await c.send(embed=e)
    else:
        c = bot.get_channel(830366314761420821)
        
        haaha = ctx.author.avatar_url
        e9 = discord.Embed(title="Oh no there was some error", description=f"`{error}`")
        e9.add_field(name="**Command Error Caused By**", value=f"{ctx.command}")
        e9.add_field(name="**By**", value=f"**ID** : {ctx.author.id}, **Name** : {ctx.author.name}")
        e9.set_thumbnail(url=f"{haaha}")
        e9.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e9, delete_after=2)
        await c.send(embed=e9)
        
        await ctx.send('**Sending the error report info to my developer**', delete_after=2)
        e = discord.Embed(title=f'In **{ctx.guild.name}**',description=f'User affected {ctx.message.author}' , color= 0x2ecc71)
        if ctx.guild.icon:
            e.set_thumbnail(url=ctx.guild.icon_url)
        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner_url_as(format="png"))
        e.add_field(name='**Total Members**',value=ctx.guild.member_count)
        e.add_field(name='**Bots**',value=sum(1 for member in ctx.guild.members if member.bot))
        e.add_field(name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True)
        e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
        await ctx.send('**Error report was successfully sent**', delete_after=2)
        await c.send(embed=e)

@bot.event
async def on_ipc_ready():
    """Called upon the IPC Server being ready"""
    print("Ipc is ready.")

@bot.event
async def on_ipc_error(endpoint, error):
    """Called upon an error being raised within an IPC route"""
    try:
        me = bot.get_user(571889108046184449)
        await me.send(str(endpoint) + " raised " + str(error))
    except:
        print(str(endpoint) + " raised " + str(error))


sentry_sdk.init(
    sentry_link,
    traces_sample_rate=1.0
)
try:
    division_by_zero = 1 / 0
except:
    pass

# import threading
# from django.core.management import call_command
# threading.Thread(target=call_command('runserver')).start()
ipc1.start()
bot.run(TOKEN)
