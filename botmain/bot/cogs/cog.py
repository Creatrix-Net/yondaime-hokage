# Discord Imports
import discord
from discord.ext import commands
from discord import Spotify
import datetime
import time
import requests
import dbl

from ..utils_dis import *

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github
        self.bot.discord_id = bot.discord_id

        self.bot.bfd = bot.bfd
        self.bot.dblst = bot.dblst
        self.bot.botlist = bot.botlist
        self.bot.topken = bot.topken
        self.bot.discordboats = bot.discordboats
        self.bot.discordbotsgg = bot.discordbotsgg
    
    async def post_guild_stats_all(self):
        guildsno = len(self.bot.guilds)+1
        members = len(set(self.bot.get_all_members()))

        dblpy = dbl.DBLClient(self.bot, self.bot.topken, autopost=True)
        await dblpy.post_guild_count(guildsno)
        b=requests.post(f'https://discordbotlist.com/api/v1/bots/{self.bot.discord_id}/stats',
            headers={'Authorization':self.bot.dblst},
            data={'guilds':guildsno,'users':members}
        )
        c=requests.post(f'https://botsfordiscord.com/api/bot/{self.bot.discord_id}',
            headers={'Authorization':self.bot.bfd,'Content-Type':'application/json'},
            json={'server_count':guildsno}
        )
        d=requests.post(f'https://api.botlist.space/v1/bots/{self.bot.discord_id}',
            headers={'Authorization':self.bot.botlist,'Content-Type':'application/json'},
            json={'server_count':guildsno}
        )
        e=requests.post(f'https://discord.boats/api/bot/{self.bot.discord_id}',
            headers={'Authorization':self.bot.discordboats},
            data={'server_count':guildsno}
        )
        f=requests.post(f'https://discord.bots.gg/api/v1/bots/{self.bot.discord_id}/stats',
            headers={'Authorization':self.bot.discordbotsgg,'Content-Type':'application/json'},
            json={'guildCount':guildsno}
        )
        r = self.bot.get_channel(822472454030229545)
        e1 = discord.Embed(title='Status posted successfully',description='[Widgets Link](https://dhruvacube.github.io/yondaime-hokage/widgets)' , color= 0x2ecc71)
        e1.set_thumbnail(url='https://i.imgur.com/Reopagp.jpg')
        e1.add_field(name='TOPGG',value='200 : [TOPGG](https://top.gg/bot/779559821162315787)')
        e1.add_field(name='DISCORDBOTLIST',value=str(b.status_code)+' : [DISCORDBOTLIST](https://discord.ly/minato-namikaze)')
        e1.add_field(name='BOTSFORDISCORD',value=str(c.status_code)+' : [BOTSFORDISCORD](https://botsfordiscord.com/bot/779559821162315787)')
        e1.add_field(name='DISCORDLIST.SPACE',value=str(d.status_code)+' : [DISCORDLIST.SPACE](https://discordlist.space/bot/779559821162315787)')
        e1.add_field(name='DISCORD.BOATS',value=str(e.status_code)+' : [DISCORD.BOATS](https://discord.boats/bot/779559821162315787)')
        e1.add_field(name='DISCORD.BOTS.GG',value=str(f.status_code)+' : [DISCORD.BOTS.GG](https://discord.bots.gg/bots/779559821162315787/)')
        await r.send(embed=e1)

    @commands.command(name='serverdump', description='Sends info to my developer that you have added me')
    @commands.cooldown(1, 1080, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    async def serverdump(self, ctx):
        '''Dumps server name to the developer'''
        c = self.bot.get_channel(813954921782706227)
        if ctx.guild.id == 747480356625711204:
            b = await ctx.send('** Okay updating info ! **')
            n=1
            for guild in ctx.bot.guilds:
                e = discord.Embed(title=f'In **{guild.name}**',description='Was added' , color= 0x2ecc71)
                if guild.icon:
                    e.set_thumbnail(url=guild.icon_url)
                if guild.banner:
                    e.set_image(url=guild.banner_url_as(format="png"))
                n+=1
                e.add_field(name='**Members**',value=f'{guild.member_count} | {sum(1 for member in guild.members if member.bot)}')
                await c.send(embed=e)
            await c.send(f'In total {n} servers')
            await ctx.send('**Updated ! Please check the <#813954921782706227>**')
        else:
            a = await ctx.send('**Sending the info to my developer**')
            e = discord.Embed(title=f'In **{ctx.guild.name}**',description=f'Bumped by {ctx.message.author}' , color= 0x2ecc71)
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner_url_as(format="png"))
            await c.send(embed=e)
            await ctx.send(f'Sent the info to developer that "I am on {ctx.guild.name}" , {ctx.author.mention} 😉')
            await self.post_guild_stats_all()

    @commands.command()
    async def spotify(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.author 
        for activity in user.activities:
            if isinstance(activity, Spotify):
                w = discord.Embed(title="Oooo, what a party!", description=f"{user.name} is listening to Spotify, let's see what!")
                w.add_field(name="Listening to?", value=f"{activity.title}")
                w.add_field(name="By?", value=f"{activity.artist}")
                w.set_thumbnail(url=activity.album_cover_url)
                return await ctx.send(embed=w)
            else:
                e = discord.Embed(title="❌ Nope, the user (you or another) aren't listening to Spotify", description=f"User {user.name} isn't listening to Spotify")
                return await ctx.send(embed=e)

    @commands.command()
    async def who(self, ctx): 
        m = WhoMenu(bot=self.bot)
        await m.start(ctx)

    @commands.command()
    async def vote(self, ctx):
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)
    
    @commands.command()
    async def uptime(self, ctx):
        current_time = time.time()
        difference = int(round(current_time - self.bot.start_time))
        text = str(datetime.timedelta(seconds=difference)) + ' mins' if str(datetime.timedelta(seconds=difference))[0]=='0' or str(datetime.timedelta(seconds=difference))[0:1]!='00' else ' hours'
        embed = discord.Embed(colour=ctx.message.author.top_role.colour)
        embed.add_field(name="Uptime", value=text)
        embed.set_footer(text=f"{ctx.author} | {self.bot.user}")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)
        

    @commands.command()
    async def ping(self, ctx):
        starttime = time.time()
        msg = await ctx.send("Ping...")
        async with ctx.channel.typing():
            e = discord.Embed(
                title="Pong!", description=f"Heartbeat : {round(self.bot.latency * 1000, 2)} ms")
            endtime = time.time()
            difference = float(int(starttime - endtime))
            e.add_field(name="Script Speed", value=f"{difference}ms")
            await msg.edit(content="", embed=e)

    @commands.command()
    async def source(self, ctx):
        """ Displays source code """
        source_url = self.bot.github
        e = discord.Embed(title="You didn't provide a command (because you cant), so here's the source!",
                          description=f"[Source]({source_url})")
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.author
        e = discord.Embed(title=f"Avatar for {user.name}")
        e.set_image(url=user.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=f'**{user}**', description=f'{user} joined **{ctx.guild.name}** at \n{user.joined_at}')
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.group()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed(
                title=f"ℹ Information Bbout **{ctx.guild.name}**", description=None)

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner_url_as(format="png"))

            embed.add_field(name="**Server Name**",
                            value=ctx.guild.name, inline=True)
            embed.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            embed.add_field(
                name="**Members**", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="**Bots**", value=find_bots, inline=True)
            embed.add_field(name="**Owner**", value=ctx.guild.owner, inline=True)
            embed.add_field(name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True)
            await ctx.send(embed=embed)

    @server.command(name="server_icon", aliases=["icon"])
    @commands.guild_only()
    async def server_icon(self, ctx):
        """ Get the current server icon """
        if not ctx.guild.icon:
            return await ctx.send("This server does not have a avatar...")
        await ctx.send(f"Avatar of **{ctx.guild.name}**\n{ctx.guild.icon_url_as(size=1024)}")

    @server.command(name="banner")
    @commands.guild_only()
    async def server_banner(self, ctx):
        """ Get the current banner image """
        if not ctx.guild.banner:
            return await ctx.send("This server does not have a banner...")
        e = discord.Embed(title=f"ℹ Banner for {ctx.guild}")
        e.set_image(url=ctx.guild.banner_url_as(format='png'))
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.author

        show_roles = ', '.join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position,
                                           reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else 'None'
        content2 = f"ℹ About **{user.id}**"
        embed = discord.Embed(
            title=content2, colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Full name", value=user, inline=True)
        embed.add_field(name="Nickname", value=user.nick if hasattr(
            user, "nick") else "None", inline=True)
        embed.add_field(name="Roles", value=show_roles, inline=False)
        embed.add_field(name="Joined", value=f"{user.joined_at}")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
