# Discord Imports
import discord
from discord.ext import commands
from discord import Spotify

# Time Imports
from datetime import datetime
import datetime
import time

# Other Imports
import random
import inspect
import os
from ..utils_dis import *

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github

    @commands.command(name='serverdump', description='Sends info to my developer that you have added me')
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def serverdump(self, ctx):
        '''Dumps server name to thr developer'''
        c = bot.get_channel(813954921782706227)
        if ctx.guild.id == 747480356625711204:
            for guild in ctx.bot.guilds:
                if not guild.id == 747480356625711204:
                    e = discord.Embed(title=f'In **{guild.name}**',description='Was added' , color= 0x2ecc71)
                    if guild.icon:
                         e.set_thumbnail(url=guild.icon_url)
                    if guild.banner:
                         e.set_image(url=guild.banner_url_as(format="png"))
        else:
            a = await ctx.send('**Sending the info to my developer')
            e = discord.Embed(title=f'In **{ctx.guild.name}**',description=f'Bumped by {ctx.message.author}' , color= 0x2ecc71)
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner_url_as(format="png"))

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
    async def lp(self, ctx, member: discord.Member = None):
        if member is None:
            starttext = "Maybe you should learn python first"
            embed2 = discord.Embed(
                title=f"{starttext}", description="Here's some tutorials! \n [Click Here For](https://automatetheboringstuff.com/) complete beginners to programming \n [Click Here For](https://learnxinyminutes.com/docs/python3/) people who know programming already \n [Click Here For](https://docs.python.org/3/tutorial/) the official tutorial\n [Click Here For](http://python.swaroopch.com/) a useful book\n [See Also For](http://www.codeabbey.com/) exercises for beginners")
            return await ctx.send(embed=embed2)
        else:
            starttext = f"Maybe you should learn python first {member.name}"
            embed = discord.Embed(
                title=f"{starttext}", description="Here's some tutorials! \n [Click Here For](https://automatetheboringstuff.com/) complete beginners to programming \n [Click Here For](https://learnxinyminutes.com/docs/python3/) people who know programming already \n [Click Here For](https://docs.python.org/3/tutorial/) the official tutorial\n [Click Here For](http://python.swaroopch.com/) a useful book\n [See Also For](http://www.codeabbey.com/) exercises for beginners")
            return await ctx.send(embed=embed)

    @commands.command()
    async def who(self, ctx): 
        m = WhoMenu(bot=self.bot)
        await m.start(ctx)

    @commands.command()
    async def vote(self, ctx):
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)
        

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
                title=f"ℹ information about **{ctx.guild.name}**", description=None)

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner_url_as(format="png"))

            embed.add_field(name="Server Name",
                            value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(
                name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=find_bots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
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
        embed.add_field(name="Joined?", value=f"{user.joined_at}")

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
