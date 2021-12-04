import datetime
import inspect
import itertools
import os

import discord
import pkg_resources
import psutil
import pygit2
from discord.ext import commands

from ...lib import Embed, PrivacyPolicy
from ...lib import time_class as time


class MySupport(commands.Cog, name="My Support"):
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.description = "Having problems with me? Then you can get the help here."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{SQUARED SOS}")

    @staticmethod
    def format_commit(commit):
        short, _, _ = commit.message.partition("\n")
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset)
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz
        )

        # [`hash`](url) message (offset)
        offset = time.format_relative(
            commit_time.astimezone(datetime.timezone.utc))
        return f"[`{short_sha2}`](https://github.com/The-4th-Hokage/yondaime-hokage/commit/{commit.hex}) {short} ({offset})"

    def get_last_commits(self, count=3):
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(
                repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count
            )
        )
        return "\n".join(self.format_commit(c) for c in commits)

    @commands.command(aliases=["stats"])
    async def about(self, ctx):
        """Tells you information about the bot itself."""
        revision = self.get_last_commits()
        embed = discord.Embed(description="Latest Changes:\n" + revision)
        embed.title = "Official Bot Server Invite"
        embed.url = "https://discord.gg/S8kzbBVN8b"
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(747480356625711204)
        owner = await self.get_or_fetch_member(support_guild, self.bot.owner_id)
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

        embed.add_field(
            name="Members", value=f"{total_members} total\n{total_unique} unique"
        )
        embed.add_field(
            name="Channels", value=f"{text + voice} total\n{text} text\n{voice} voice"
        )

        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(
            name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU"
        )

        version = pkg_resources.get_distribution("discord.py").version
        embed.add_field(name="Guilds", value=guilds)
        embed.add_field(name="Uptime", value=self.bot.uptime)
        embed.add_field(
            name="**Bot Developers:**",
            value=f"[{ctx.get_user(self.bot.owner_id)}](https://discord.com/users/{self.bot.owner_id}/)",
        )
        embed.add_field(
            name="**More Info:**",
            value="[Click Here](https://statcord.com/bot/779559821162315787)",
        )
        embed.add_field(
            name="**Incidents/Maintenance Reports:**",
            value="[Click Here](https://minatonamikaze.statuspage.io/)",
        )
        embed.set_footer(
            text=f"Made with discord.py v{version}",
            icon_url="http://i.imgur.com/5BFecvA.png",
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command(description="Generates my invite link for your server")
    async def inviteme(self, ctx):
        """Generates my invite link for your server"""
        embed = discord.Embed(
            title="**Invite Link**",
            description="[My Invite Link!](https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=8&redirect_uri=https%3A%2F%2Fminatonamikaze-invites.herokuapp.com%2Finvite&scope=applications.commands%20bot&response_type=code&state=cube12345%3F%2FDirect%20From%20Bot)",
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(description="Generates my support server invite")
    async def supportserver(self, ctx):
        """Generates my support server invite"""
        await ctx.send("**Here you go, my support server invite**")
        await ctx.send("https://discord.gg/S8kzbBVN8b")

    @commands.command()
    async def privacy(self, ctx):
        """Get the Privacy Policy"""
        m = PrivacyPolicy(bot=self.bot)
        await m.start(ctx)

    @commands.command()
    async def ping(self, ctx):
        """Get the Latency"""
        starttime = time.time()
        msg = await ctx.send(":ping_pong: Ping... :ping_pong:")
        async with ctx.channel.typing():
            e = Embed(
                title=":ping_pong: Pong! :ping_pong:",
                description=f"Heartbeat : {round(self.bot.latency * 1000, 2)} ms",
            )
            endtime = time.time()
            difference = float(int(starttime - endtime))
            e.add_field(
                name=":inbox_tray: Script Speed :outbox_tray:", value=f"{difference}ms"
            )
            e.set_image(
                url="https://cdn.discordapp.com/attachments/777918705098686465/870692724880334878/pong_9.gif"
            )
            await msg.edit(content="", embed=e)

    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = "https://github.com/The-4th-Hokage/yondaime-hokage"
        branch = "master"
        if command is None:
            return await ctx.send(source_url)

        if command == "help":
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace(".", " "))
            if obj is None:
                return await ctx.send("Could not find command.")

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith("discord"):
            # not a built-in command
            location = os.path.relpath(filename).replace("\\", "/")
        else:
            location = module.replace(".", "/") + ".py"
            source_url = "https://github.com/StockerMC/discord.py"
            branch = "master"

        final_url = f"<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)


def setup(bot):
    bot.add_cog(MySupport(bot))
