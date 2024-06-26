from __future__ import annotations

import datetime
import inspect
import itertools
import logging
import os
from typing import TYPE_CHECKING

import discord
import pkg_resources
import psutil
import pygit2
from discord.ext import commands

from minato_namikaze.lib import ChannelAndMessageId
from minato_namikaze.lib import Embed
from minato_namikaze.lib import LinksAndVars
from minato_namikaze.lib import PrivacyPolicy
from minato_namikaze.lib import time_class as time
from minato_namikaze.lib import VotingMenu

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib import Context

    from ... import MinatoNamikazeBot


class MySupport(commands.Cog, name="My Support"):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.process = psutil.Process()
        self.description = "Having problems with me? Then you can get the help here."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{SQUARED SOS}")

    @commands.command()
    async def vote(self, ctx: "Context"):
        """Get all the voting links"""
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)

    @staticmethod
    def format_commit(commit):
        short, _, _ = commit.message.partition("\n")
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset),
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz,
        )

        # [`hash`](url) message (offset)
        offset = time.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f"[`{short_sha2}`]({LinksAndVars.github.value}/commit/{commit.hex}) {short} ({offset})"

    def get_last_commits(self, count=3):
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(
                repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL),
                count,
            ),
        )
        return "\n".join(self.format_commit(c) for c in commits)

    @commands.command(aliases=["stats"])
    async def about(self, ctx: "Context"):
        """Tells you information about the bot itself."""
        revision = self.get_last_commits()
        embed = discord.Embed(description="Latest Changes:\n" + revision)
        embed.title = "Official Bot Server Invite"
        embed.url = f"https://discord.gg/{LinksAndVars.invite_code.value}"
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(ChannelAndMessageId.server_id2.value)
        owner = await self.bot.get_or_fetch_member(
            support_guild,
            self.bot.application_id,
        )
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
            name="Members",
            value=f"{total_members} total\n{total_unique} unique",
        )
        embed.add_field(
            name="Channels",
            value=f"{text + voice} total\n{text} text\n{voice} voice",
        )

        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(
            name="Process",
            value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU",
        )

        version = pkg_resources.get_distribution("discord.py").version
        embed.add_field(name="Guilds", value=guilds)
        embed.add_field(name="Uptime", value=self.bot.uptime)
        embed.add_field(
            name="Developer",
            value=f"[{ctx.get_user(self.bot.owner_id)}](https://discord.com/users/{self.bot.owner_id})",
        )
        embed.add_field(
            name="More Info",
            value=f"[Click Here](https://statcord.com/bot/{self.bot.application_id})",
        )
        embed.add_field(
            name="Incidents/Maintenance Reports",
            value=f"[Click Here]({LinksAndVars.statuspage_link.value})",
        )
        embed.add_field(
            name="Website",
            value=f"[Click Here]({LinksAndVars.website.value})",
        )
        embed.set_footer(
            text=f"Made with discord.py v{version}",
            icon_url="https://i.imgur.com/5BFecvA.png",
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command(
        description="Generates my invite link for your server",
        aliases=["invite"],
    )
    async def inviteme(self, ctx: "Context"):
        """Generates my invite link for your server"""
        embed = discord.Embed(
            title="Invite Link",
            description=f":point_right: [Required Perms Invite]({self.bot.get_required_perms_invite_link}) \n :point_right: [Admin Perms Invite]({self.bot.get_admin_invite_link})",
        )
        embed.set_thumbnail(url=ctx.bot.user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(description="Generates my support server invite")
    async def supportserver(self, ctx: "Context"):
        """Generates my support server invite"""
        await ctx.send(
            f"**Here you go, my support server invite**\nhttps://discord.gg/{LinksAndVars.invite_code.value}",
        )

    @commands.command()
    async def privacy(self, ctx: "Context"):
        """Get the Privacy Policy"""
        m = PrivacyPolicy(bot=self.bot)
        await m.start(ctx)

    @commands.command()
    async def ping(self, ctx: "Context"):
        """Get the Latency"""
        msg = await ctx.send(":ping_pong: Ping... :ping_pong:")
        async with ctx.channel.typing():
            e = Embed(
                title=":ping_pong: Pong! :ping_pong:",
                description=f"Heartbeat : {round(self.bot.latency * 1000, 2)} ms",
            )
            e.add_field(
                name=":inbox_tray: Script Speed :outbox_tray:",
                value=f"{round(self.bot.latency,5)}ms",
            )
            e.set_image(url=await self.bot.get_random_image_from_tag("ping pong anime"))
            await msg.edit(content="", embed=e)
        return

    @commands.command()
    async def source(self, ctx: "Context", *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = LinksAndVars.github.value
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
            source_url = LinksAndVars.github.value
        repo = pygit2.Repository(".git")
        commits = list(
            itertools.islice(
                repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL),
                1,
            ),
        )
        final_url = f"<{source_url}/blob/{commits[0].hex}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>"
        await ctx.send(final_url)


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(MySupport(bot))
