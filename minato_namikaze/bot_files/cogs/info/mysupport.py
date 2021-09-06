import platform

import discord, datetime
import DiscordUtils
import psutil, pygit2, itertools
from discord.ext import commands
from psutil._common import bytes2human
import pkg_resources

from ...lib import Embed, get_user, get_or_fetch_member
from ...lib import time_class as time


class MySupport(commands.Cog, name="My Support"):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.description = 'Having problems with me? Then you can get the help here.'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{SQUARED SOS}')
    
    def format_commit(self, commit):
        short, _, _ = commit.message.partition('\n')
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)

        # [`hash`](url) message (offset)
        offset = time.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f'[`{short_sha2}`](https://github.com/The-4th-Hokage/yondaime-hokage/commit/{commit.hex}) {short} ({offset})'
    
    def get_last_commits(self, count=3):
        repo = pygit2.Repository('.git')
        commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return '\n'.join(self.format_commit(c) for c in commits)
    
    @commands.command()
    async def about(self, ctx):
        """Tells you information about the bot itself."""

        revision = self.get_last_commits()
        embed = discord.Embed(description='Latest Changes:\n' + revision)
        embed.title = 'Official Bot Server Invite'
        embed.url = 'https://discord.gg/S8kzbBVN8b'
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(747480356625711204)
        owner = await get_or_fetch_member(support_guild, self.bot.owner_id)
        embed.set_author(name=str(owner), icon_url=owner.display_avatar.url)

        # statistics
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable:
                continue

            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        embed.add_field(name='Members', value=f'{total_members} total\n{total_unique} unique')
        embed.add_field(name='Channels', value=f'{text + voice} total\n{text} text\n{voice} voice')

        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU')

        version = pkg_resources.get_distribution('discord.py').version
        embed.add_field(name='Guilds', value=guilds)
        embed.add_field(name='Uptime', value=self.bot.uptime)
        embed.set_footer(text=f'Made with discord.py v{version}', icon_url='http://i.imgur.com/5BFecvA.png')
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command(description='Generates my invite link for your server')
    async def inviteme(self, ctx):
        '''Generates my invite link for your server'''
        embed = discord.Embed(
            title='**Invite Link**', description=f'[My Invite Link!](https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&redirect_uri=https%3A%2F%2Fminatonamikaze-invites.herokuapp.com%2Finvite&scope=applications.commands%20bot&response_type=code&state=cube12345%3F%2FDirect%20From%20Bot)')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(description='Generates my support server invite')
    async def supportserver(self, ctx):
        '''Generates my support server invite'''
        await ctx.send('**Here you go, my support server invite**')
        await ctx.send('https://discord.gg/S8kzbBVN8b')

    @commands.command(name="stats", description="A usefull command that displays bot statistics.")
    async def stats(self, ctx):
        '''Get the stats for the me'''
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour or discord.Color.random(),
            timestamp=ctx.message.created_at,
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(name="**Bot Version:**", value=self.bot.version)
        embed.add_field(name="**Python Version:**", value=pythonVersion)
        embed.add_field(name="**Discord.Py Version**", value=dpyVersion)
        embed.add_field(name="**Total Guilds:**", value=serverCount+1)
        embed.add_field(name="**Total Users:**", value=memberCount)
        embed.add_field(name="**Bot Developers:**",
                        value=f"[{get_user(self.bot.owner_id, ctx)}](https://discord.com/users/{self.bot.owner_id}/)")
        embed.add_field(name="**More Info:**",
                        value="[Click Here](https://statcord.com/bot/779559821162315787)")
        embed.add_field(name="**Incidents/Maintenance Reports:**",
                        value="[Click Here](https://minatonamikaze.statuspage.io/)")

        embed.set_footer(text=f"{ctx.author} | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="cpu_status", description="Display CPU stats of the bot.")
    async def cpu_status(self, ctx):
        '''Display CPU Stats'''
        cpu = Embed(title='CPU Stats :computer:')
        cpu.add_field(name='**CPU Usage** :alarm_clock:',
                      value=f'{psutil.cpu_percent()} %', inline=True)

        ram = Embed(title='RAM Stats :chart_with_upwards_trend:')
        ram.add_field(name="**Total RAM :repeat_one:**",
                      value=bytes2human(psutil.virtual_memory()[0]))
        ram.add_field(name="**RAM Available :floppy_disk:**",
                      value=bytes2human(psutil.virtual_memory()[1]))
        ram.add_field(name="**RAM % use**",
                      value=bytes2human(psutil.virtual_memory()[2]))
        ram.add_field(name="**RAM Used :card_box:**",
                      value=bytes2human(psutil.virtual_memory()[3]))
        ram.add_field(name="**RAM :free:**",
                      value=bytes2human(psutil.virtual_memory()[4]))

        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run([cpu, ram])


def setup(bot):
    bot.add_cog(MySupport(bot))
