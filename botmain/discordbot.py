import os
import time
from os.path import join
from pathlib import Path

import aiozaneapi
import async_cleverbot as ac
import discord
import dotenv
import mystbin
from asyncdagpi import Client
from discord.ext import commands
from discord.ext.buttons import Paginator
import dbl
import requests


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

bot = commands.Bot(command_prefix=commands.when_mentioned_or(')'),intents=intents, help_command=Help(),  allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),case_insensitive=True,description="Hi I am **Minato Namikaze**, Yondaime Hokage")
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
bot.discordbotlist = token_get('DBLST')
bot.thresholds = (10, 25, 50, 100)
bot.description = "Myself **Minato Namikaze** Aka **Yondaime Hokage** ||私の湊波風別名第四火影||"
bot.DEFAULT_GIF_LIST_PATH = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')

bot.topgg = token_get('TOPGG')
bot.dblst = token_get('DISCORDBOTLIST')
bot.botlist = token_get('BOTLISTSPACE')
bot.bfd = token_get('BOTSFORDISCORD')
bot.discordboats = token_get('DISCORDBOATS')
bot.discordbotsgg = token_get('DISCORDBOTS')
bot.discordlistology = token_get('DISCORDLISTOLOGY')
bot.discordextremelist = token_get('DISCORDEXTREMELIST')
bot.spacebot = token_get('SPACEBOT')

minato_dir = Path(__file__).resolve(strict=True).parent / join('bot','discord_bot_images')
minato_gif = [f for f in os.listdir(join(minato_dir ,'minato'))]
    

async def post_guild_stats_all():
    guildsno = len(bot.guilds)+1
    members = len(set(bot.get_all_members()))
    imageslistdir = Path(__file__).resolve(strict=True).parent / join('bot','images_list.txt')
    filepointer=open(imageslistdir)
    imageslist = filepointer.readlines()

    dblpy = dbl.DBLClient(bot, bot.topken, autopost=True)
    await dblpy.post_guild_count(guildsno)
    b=requests.post(f'https://discordbotlist.com/api/v1/bots/{bot.discord_id}/stats',
        headers={'Authorization':bot.dblst},
        data={'guilds':guildsno,'users':members}
    )
    c=requests.post(f'https://botsfordiscord.com/api/bot/{bot.discord_id}',
        headers={'Authorization':bot.bfd,'Content-Type':'application/json'},
        json={'server_count':guildsno}
    )
    d=requests.post(f'https://api.botlist.space/v1/bots/{bot.discord_id}',
        headers={'Authorization':bot.botlist,'Content-Type':'application/json'},
        json={'server_count':guildsno}
    )
    e=requests.post(f'https://discord.boats/api/bot/{bot.discord_id}',
        headers={'Authorization':bot.discordboats},
        data={'server_count':guildsno}
    )
    f=requests.post(f'https://discord.bots.gg/api/v1/bots/{bot.discord_id}/stats',
        headers={'Authorization':bot.discordbotsgg,'Content-Type':'application/json'},
        json={'guildCount':guildsno}
    )
    g=requests.post(f'https://discordlistology.com/api/v1/bots/{bot.discord_id}/stats',
        headers={'Authorization':bot.discordlistology},
        data={'servers':guildsno}
    )
    
    h=requests.post(f'https://space-bot-list.xyz/api/bots/{bot.discord_id}', 
        headers = {"Authorization": bot.spacebot, "Content-Type": "application/json"}, 
        json = {"guilds": guildsno, "users": members})
    
    r = bot.get_channel(822472454030229545)
    e1 = discord.Embed(title='Status posted successfully',description='[Widgets Link](https://dhruvacube.github.io/yondaime-hokage/widgets)' , color= 0x2ecc71)
    e1.set_image(url=random.choice(imageslist).strip('\n'))
    e1.set_thumbnail(url='https://i.imgur.com/Reopagp.jpg')
    e1.add_field(name='TopGG',value='200 : [TopGG](https://top.gg/bot/779559821162315787)')
    e1.add_field(name='DiscordBotList',value=str(b.status_code)+' : [DiscordBotList](https://discord.ly/minato-namikaze)')
    e1.add_field(name='BotsForDiscord',value=str(c.status_code)+' : [BotsForDiscord](https://botsfordiscord.com/bot/779559821162315787)')
    e1.add_field(name='DiscordListSpace',value=str(d.status_code)+' : [DiscordListSpace](https://discordlist.space/bot/779559821162315787)')
    e1.add_field(name='DiscordBoats',value=str(e.status_code)+' : [DiscordBoats](https://discord.boats/bot/779559821162315787)')
    e1.add_field(name='DiscordBots',value=str(f.status_code)+' : [DiscordBots](https://discord.bots.gg/bots/779559821162315787/)')
    e1.add_field(name='DiscordListoLogy',value=str(g.status_code)+' : [DiscordListoLogy](https://discordlistology.com/bots/779559821162315787)')
    e1.add_field(name='Space Bots',value=str(h.status_code)+' : [Space Bots](https://space-bot-list.xyz/bots/779559821162315787)')
    await r.send(embed=e1)

# Events
@bot.event
async def on_ready():
    for filename in os.listdir(Path(__file__).resolve(strict=True).parent / join('bot','cogs')):
        if filename.endswith('.py'):
            if filename != 'music.py':
                bot.load_extension(f'bot.cogs.{filename[:-3]}')
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name='over Naruto'))

    current_time = time.time()
    difference = int(round(current_time - bot.start_time))
    stats = bot.get_channel(819128718152695878)
    e = discord.Embed(title=f"Bot Loaded!", description=f"Bot ready by **{time.ctime()}**, loaded all cogs perfectly! Time to load is {difference} secs :)")
    e.set_thumbnail(url='https://i.imgur.com/fMx8iil.jpg')
    print('Started The Bot')

    await stats.send(embed=e) 

#on join send message event
@bot.event
async def on_guild_join(guild):
    try:
        img=random.choice(minato_gif)
        file = discord.File(join(minato_dir, 'minato',img), filename=img)
        await guild.system_channel.send(file=file)

        f=open(Path(__file__).resolve(strict=True).parent / join('bot','welcome_message.txt'),'r')
        f1=f.read()
        await guild.system_channel.send(f1.format(guild.name, bot.user.mention, bot.user.mention, bot.user.mention, guild.owner.mention))

        '''
        if guild.id not in (568567800910839811 , 632908146305925129):
            await guild.system_channel.send(f'----------')
            await guild.system_channel.send('My **sleeping time** is from')
            await guild.system_channel.send('**00:00 AM IST**  to')
            await guild.system_channel.send('**07:00 AM IST**')
        '''
        
        img=random.choice(minato_gif)
        file = discord.File(join(minato_dir, 'minato',img), filename=img)
        await guild.system_channel.send(file=file)
    except: pass
    await post_guild_stats_all()

    e34= discord.Embed(title=f'{guild.name}', color= 0x2ecc71,description='Added')
    if guild.icon:
        e34.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        e34.set_image(url=guild.banner_url_as(format="png"))
    c = bot.get_channel(813954921782706227)
    e34.add_field(name='**Members**',value=f'{guild.member_count} | {sum(1 for member in guild.members if member.bot)}')
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
    await post_guild_stats_all()

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
    if bot.user.mentioned_in(message) and message.mention_everyone is False and message.content.lower() in ('<@!779559821162315787>', '<@779559821162315787>') or message.content.lower() in ('<@!779559821162315787> prefix', '<@779559821162315787> prefix'):
        if not message.author.bot:
            await  message.channel.send('The prefix is **)** ,A full list of all commands is available by typing ```)help```')
    if message.channel.id == 814134179049635840:
        embed = message.embeds[0].to_dict()
        
        for guild in bot.guilds:
            try:
                if not guild.id == 747480356625711204: 
                    e = discord.Embed(title=embed['title'],description=embed['description'] , color= 0x2ecc71)
                    e.set_thumbnail(url='https://i.imgur.com/lwGawEv.jpeg')
                    e.add_field(name='**Members**',value=f'{guild.member_count} | {sum(1 for member in guild.members if member.bot)}')
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
        await ctx.send(embed=e3)
    elif isinstance(error, commands.MissingRequiredArgument):
        e4 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e4.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e4)

    elif isinstance(error, commands.CommandInvokeError):
        perms= 8 #1073737719 #2147483656
        e7 = discord.Embed(title="Oh no, I guess I have not been given proper access!", description=f"`{error}`")
        e7 = discord.Embed(title="Oh no, I guess I have not been given proper access! Or some internal error", description=f"`{error}`")
        e7.add_field(name="Command Error Caused By:", value=f"{ctx.command}")
        e7.add_field(name="By", value=f"{ctx.author.name}")
        e7.add_field(name="MY INVITE LINK", value=f"[LINK](https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions={perms}&scope=bot)")
        e7.set_thumbnail(url=f"https://i.imgur.com/1zey3je.jpg")
        e7.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e7)
    '''
    else:
        haaha = ctx.author.avatar_url
        e9 = discord.Embed(title="Oh no there was some error", description=f"`{error}`")
        e9.add_field(name="**Command Error Caused By**", value=f"{ctx.command}")
        e9.add_field(name="**By**", value=f"**ID** : {ctx.author.id}, **Name** : {ctx.author.name}")
        e9.set_thumbnail(url=f"{haaha}")
        e9.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e9)

    elif isinstance(error, commands.CommandNotFound):
        e2 = discord.Embed(title="Command Error!", description=f"`{error}`")
        e2.set_footer(text=f"{ctx.author.name}")
        await ctx.channel.send(embed=e2)
    '''

bot.run(TOKEN)
