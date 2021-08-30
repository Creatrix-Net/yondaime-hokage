# Discord Imports
import datetime
import time

import discord
from discord import Spotify
from discord.ext import commands

from ...lib import Embed, PrivacyPolicy


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github

        self.description = "Get's the Information about the server"
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{INFORMATION SOURCE}')

    @commands.command(name='serverdump', description='Sends info to my developer that you have added me')
    @commands.cooldown(1, 1080, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def serverdump(self, ctx):
        '''Dumps server name to the developer'''
        c = self.bot.get_channel(
            813954921782706227) if not self.bot.local else self.bot.get_channel(869238107524968479)
        if ctx.guild.id in (747480356625711204, 869085099470225508):
            b = await ctx.send('** Okay updating info ! **')
            n = 1
            for guild in ctx.bot.guilds:
                e = discord.Embed(
                    title=f'In **{guild.name}**', description='Was added', color=discord.Color.green())
                if guild.icon:
                    e.set_thumbnail(url=guild.icon_url)
                if guild.banner:
                    e.set_image(url=guild.banner_url_as(format="png"))
                n += 1
                e.add_field(name='**Total Members**', value=guild.member_count)
                e.add_field(
                    name='**Bots**', value=sum(1 for member in guild.members if member.bot))
                e.add_field(name="**Region**",
                            value=str(guild.region).capitalize(), inline=True)
                e.add_field(name="**Server ID**", value=guild.id, inline=True)
                await c.send(embed=e)
            await c.send(f'In total {n} servers')
            await ctx.send('**Updated ! Please check the <#813954921782706227>**')
        else:
            a = await ctx.send('**Sending the info to my developer**')
            e = discord.Embed(
                title=f'In **{ctx.guild.name}**', description=f'Bumped by **{ctx.message.author}**', color=0x2ecc71)
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner_url_as(format="png"))
            e.add_field(name='**Total Members**', value=ctx.guild.member_count)
            e.add_field(
                name='**Bots**', value=sum(1 for member in ctx.guild.members if member.bot))
            e.add_field(name="**Region**",
                        value=str(ctx.guild.region).capitalize(), inline=True)
            e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            await c.send(embed=e)
            await ctx.send(f'Sent the info to developer that "**I am in __{ctx.guild.name}__ guild**" , {ctx.author.mention} 😉')

    '''
    @commands.command()
    async def spotify(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.author 
        for activity in user.activities:
            if isinstance(activity, Spotify):
                w = discord.Embed(title="Oooo, what a party!", description=f"{user.name} is listening to Spotify, let's see what!")
                w.add_field(name="**Listening to**", value=f"{activity.title}")
                w.add_field(name="**By**", value=f"{activity.artist}")
                w.set_thumbnail(url=activity.album_cover_url)
                return await ctx.send(embed=w)
            else:
                e = discord.Embed(title="❌ Nope, the user (you or another) aren't listening to Spotify", description=f"User {user.name} isn't listening to Spotify")
                return await ctx.send(embed=e)
    '''

    @commands.command()
    async def privacy(self, ctx):
        '''Get the Privacy Policy'''
        m = PrivacyPolicy(bot=self.bot)
        await m.start(ctx)

    @commands.command()
    async def uptime(self, ctx):
        '''Get the uptime in hours for me'''
        current_time = time.time()
        difference = int(round(current_time - self.bot.start_time))
        text = str(datetime.timedelta(seconds=difference)) + ' mins' if str(datetime.timedelta(seconds=difference)
                                                                            )[0] == '0' or str(datetime.timedelta(seconds=difference))[0:1] != '00' else ' hours'
        embed = discord.Embed(colour=ctx.message.author.top_role.colour)
        embed.add_field(name="Uptime", value=text)
        embed.set_footer(text=f"{ctx.author} | {self.bot.user}")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("Current uptime: " + text)

    # @cog_ext.cog_slash(name="ping")
    @commands.command()
    async def ping(self, ctx):
        '''Get the Latency'''
        starttime = time.time()
        msg = await ctx.send(":ping_pong: Ping... :ping_pong:")
        async with ctx.channel.typing():
            e = Embed(
                title=":ping_pong: Pong! :ping_pong:", description=f"Heartbeat : {round(self.bot.latency * 1000, 2)} ms")
            endtime = time.time()
            difference = float(int(starttime - endtime))
            e.add_field(name=":inbox_tray: Script Speed :outbox_tray:",
                        value=f"{difference}ms")
            e.set_image(url='https://cdn.discordapp.com/attachments/777918705098686465/870692724880334878/pong_9.gif')
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
                title=f"ℹ Information About **{ctx.guild.name}**", description=None)

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner_url_as(format="png"))

            embed.add_field(name="**Server Name**",
                            value=ctx.guild.name, inline=True)
            embed.add_field(name="**Server ID**",
                            value=ctx.guild.id, inline=True)
            embed.add_field(
                name="**Members**", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="**Bots**", value=find_bots, inline=True)
            embed.add_field(name="**Owner**",
                            value=ctx.guild.owner, inline=True)
            embed.add_field(
                name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True)
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
        e = Embed(title=f"ℹ Banner for {ctx.guild}")
        e.set_image(url=ctx.guild.banner_url_as(format='png'))
        await ctx.send(embed=e)

    @commands.command(aliases=['whois','who'])
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
