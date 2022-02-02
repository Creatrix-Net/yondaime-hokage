import ast
import asyncio
import logging
import os
import time
from os.path import join
from pathlib import Path

import TenGiphPy

try:
    import uvloop
except ImportError:
    pass

import random
from collections import Counter, defaultdict, deque
from datetime import datetime
from typing import Optional, Union

import discord
import dotenv
import sentry_sdk
from discord.ext import commands
from DiscordDatabase import DiscordDatabase
from lib import (
    BASE_DIR,
    ChannelAndMessageId,
    Context,
    Embed,
    LinksAndVars,
    PaginatedHelpCommand,
    PostStats,
    Tokens,
    api_image_store_dir,
    format_dt,
    format_relative,
)
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

dotenv_file = os.path.join(Path(__file__).resolve().parent.parent / ".env")


def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname, "False").strip("\n")


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = [")", "m!", "minato", "minato "]

    if not message.guild:
        return "m!"

    return commands.when_mentioned_or(*prefixes)(bot, message)


class MinatoNamikazeBot(commands.AutoShardedBot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=True,
                                                   everyone=True,
                                                   users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
        ).all()
        self._cache = {}

        self.version = str(token_get("BOT_VER"))
        self.local = ast.literal_eval(token_get("LOCAL"))

        self.start_time = discord.utils.utcnow()
        self.github = token_get("GITHUB")

        self._prev_events = deque(maxlen=10)

        # shard_id: List[datetime.datetime]
        # shows the last attempted IDENTIFYs and RESUMEs
        self.resumes = defaultdict(list)
        self.identifies = defaultdict(list)

        self.spam_control = commands.CooldownMapping.from_cooldown(
            10, 12.0, commands.BucketType.user)
        self._auto_spam_count = Counter()

        self.db = DiscordDatabase(self, ChannelAndMessageId.server_id2.value)

        self.uptime = format_relative(self.start_time)

        super().__init__(
            command_prefix=get_prefix,
            description="Konichiwa, myself Minato Namikaze, Konohagakure Yondaime Hokage, I try my best to do every work as a Hokage!",
            chunk_guilds_at_startup=False,
            heartbeat_timeout=150.0,
            pm_help=None,
            help_attrs=dict(hidden=True),
            allowed_mentions=allowed_mentions,
            intents=intents,
            enable_debug_events=True,
            help_command=PaginatedHelpCommand(),
            owner_id=LinksAndVars.owner_ids.value[0],
        )

    def run(self):
        try:

            sentry_sdk.init(
                Tokens.sentry_link.value,
                traces_sample_rate=1.0,
                integrations=[
                    AioHttpIntegration(),
                    ThreadingIntegration(),
                    LoggingIntegration(),
                    ModulesIntegration(),
                ],
            )
            log.info("Sentry Setup Done")
            log.info("Bot will now start")
            super().run(Tokens.token.value, reconnect=True)
        except discord.PrivilegedIntentsRequired:
            log.critical(
                "[Login Failure] You need to enable the server members intent on the Discord Developers Portal."
            )
        except discord.errors.LoginFailure:
            log.critical(
                "[Login Failure] The token initialsed in environment(or .env file) is invalid."
            )
        except KeyboardInterrupt:
            log.critical(
                "The bot is shutting down since force shutdown was initiated.")
        except Exception as e:
            log.critical("An exception occured, %s", e)

    async def on_ready(self):
        if not os.path.isdir(api_image_store_dir):
            os.mkdir(api_image_store_dir)

        cog_dir = BASE_DIR / "cogs"
        for filename in list(set(os.listdir(cog_dir))):
            if os.path.isdir(cog_dir / filename):
                for i in os.listdir(cog_dir / filename):
                    if i.endswith(".py"):
                        self.load_extension(
                            f'cogs.{filename.strip(" ")}.{i[:-3]}')
            else:
                if filename.endswith(".py"):
                    self.load_extension(f"cogs.{filename[:-3]}")
        self.load_extension("jishaku")

        difference = int(round(time.time() - self.start_time.timestamp()))
        stats = (self.get_channel(
            ChannelAndMessageId.restartlog_channel1.value)
            if not self.local else self.get_channel(
            ChannelAndMessageId.restartlog_channel2.value))
        e = Embed(
            title="Bot Loaded!",
            description=f"Bot ready by **{format_dt(datetime.now(), 'R',True)}**, loaded all cogs perfectly! Time to load is {difference} secs :)",
        )
        e.set_thumbnail(url=self.user.avatar.url)

        guild = (self.get_guild(ChannelAndMessageId.server_id.value)
                 if not self.local else self.get_channel(
                     ChannelAndMessageId.restartlog_channel2.value))
        try:
            self._cache[guild.id] = {}
            for invite in await guild.invites():
                self._cache[guild.id][invite.code] = invite
        except:
            pass
        log.info("Started The Bot")

        try:
            await stats.send(embed=e)
        except:
            pass
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(type=discord.ActivityType.watching,
                                      name="over Naruto"),
        )

        if ast.literal_eval(token_get("POST_STATS")):
            await self.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name="over Naruto"),
            )
            await PostStats(self).post_guild_stats_all()
            log.info("Status Posted")
            await PostStats(self).post_commands()
            log.info("Commands Status Posted")

            await self.change_presence(
                status=discord.Status.idle,
                activity=discord.Activity(type=discord.ActivityType.watching,
                                          name="over Naruto"),
            )

    async def query_member_named(self, guild, argument, *, cache=False):
        """Queries a member by their name, name + discrim, or nickname.
        Parameters
        ------------
        guild: Guild
            The guild to query the member in.
        argument: str
            The name, nickname, or name + discrim combo to check.
        cache: bool
            Whether to cache the results of the query.
        Returns
        ---------
        Optional[Member]
            The member matching the query or None if not found.
        """
        if len(argument) > 5 and argument[-5] == "#":
            username, _, discriminator = argument.rpartition("#")
            members = await guild.query_members(username,
                                                limit=100,
                                                cache=cache)
            return discord.utils.get(members,
                                     name=username,
                                     discriminator=discriminator)
        else:
            members = await guild.query_members(argument,
                                                limit=100,
                                                cache=cache)
            return discord.utils.find(lambda m: argument in (m.name, m.nick),
                                      members)

    async def get_or_fetch_member(self, guild, member_id):
        """Looks up a member in cache or fetches if not found.
        Parameters
        -----------
        guild: Guild
            The guild to look in.
        member_id: int
            The member ID to search for.
        Returns
        ---------
        Optional[Member]
            The member or None if not found.
        """

        member = guild.get_member(member_id)
        if member is not None:
            return member

        shard = self.get_shard(guild.shard_id)
        if shard.is_ws_ratelimited():
            try:
                member = await guild.fetch_member(member_id)
            except discord.HTTPException:
                return None
            else:
                return member

        members = await guild.query_members(limit=1,
                                            user_ids=[member_id],
                                            cache=True)
        if not members:
            return None
        return members[0]

    async def resolve_member_ids(self, guild, member_ids):
        """Bulk resolves member IDs to member instances, if possible.
        Members that can't be resolved are discarded from the list.
        This is done lazily using an asynchronous iterator.
        Note that the order of the resolved members is not the same as the input.
        Parameters
        -----------
        guild: Guild
            The guild to resolve from.
        member_ids: Iterable[int]
            An iterable of member IDs.
        Yields
        --------
        Member
            The resolved members.
        """

        needs_resolution = []
        for member_id in member_ids:
            member = guild.get_member(member_id)
            if member is not None:
                yield member
            else:
                needs_resolution.append(member_id)

        total_need_resolution = len(needs_resolution)
        if total_need_resolution == 1:
            shard = self.get_shard(guild.shard_id)
            if shard.is_ws_ratelimited():
                try:
                    member = await guild.fetch_member(needs_resolution[0])
                except discord.HTTPException:
                    pass
                else:
                    yield member
            else:
                members = await guild.query_members(limit=1,
                                                    user_ids=needs_resolution,
                                                    cache=True)
                if members:
                    yield members[0]
        elif total_need_resolution <= 100:
            # Only a single resolution call needed here
            resolved = await guild.query_members(limit=100,
                                                 user_ids=needs_resolution,
                                                 cache=True)
            for member in resolved:
                yield member
        else:
            # We need to chunk these in bits of 100...
            for index in range(0, total_need_resolution, 100):
                to_resolve = needs_resolution[index:index + 100]
                members = await guild.query_members(limit=100,
                                                    user_ids=to_resolve,
                                                    cache=True)
                for member in members:
                    yield member

    async def on_shard_resumed(self, shard_id):
        log.info(f"Shard ID {shard_id} has resumed...")
        self.resumes[shard_id].append(discord.utils.utcnow())

    async def close(self):
        await super().close()

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return

        try:
            await self.invoke(ctx)
        except:
            pass

    async def get_bot_inviter(self, guild: discord.Guild):
        try:
            async for i in guild.audit_logs(limit=1):
                return i.user
        except:
            return guild.owner

    async def get_welcome_channel(
        self,
        guild: discord.Guild,
        inviter_or_guild_owner: Union[discord.User, discord.Member],
    ):
        try:
            return guild.system_channel
        except:
            try:
                text_channels_list = guild.text_channels
                for i in text_channels_list:
                    if i.permissions_for(self.user).send_messages:
                        return i
            except:
                return inviter_or_guild_owner

    @property
    def get_admin_invite_link(self):
        return f"https://discord.com/oauth2/authorize?client_id={self.application_id}&permissions=8&redirect_uri=https%3A%2F%2Fminatonamikaze-invites.herokuapp.com%2Finvite&scope=applications.commands%20bot&response_type=code&state=cube12345%3F%2FDirect%20From%20Bot"

    @property
    def get_required_perms_invite_link(self):
        return f"https://discord.com/oauth2/authorize?client_id={self.application_id}&permissions=1515049189367&redirect_uri=https%3A%2F%2Fminatonamikaze-invites.herokuapp.com%2Finvite&scope=applications.commands%20bot&response_type=code&state=cube12345%3F%2FDirect%20From%20Bot"

    def get_random_image_from_tag(self, tag_name: str) -> Optional[str]:
        tenor_giphy = ["tenor", "giphy"]
        if random.choice(tenor_giphy) == "tenor":
            api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
            try:
                return api_model.random(str(tag_name.lower()))
            except:
                return
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return api_model.random(str(
                tag_name.lower()))["data"]["images"]["downsized_large"]["url"]
        except:
            return

    async def get_random_image_from_tag(self, tag_name: str) -> Optional[str]:
        tenor_giphy = ["tenor", "giphy"]
        if random.choice(tenor_giphy) == "tenor":
            api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
            try:
                return await api_model.arandom(str(tag_name.lower()))
            except:
                return
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return (await api_model.arandom(
                tag=str(tag_name.lower())
            ))["data"]["images"]["downsized_large"]["url"]
        except:
            return

    def tenor(self, tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
        try:
            return api_model.random(str(tag_name.lower()))
        except:
            return

    def giphy(self, tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return api_model.random(str(
                tag_name.lower()))["data"]["images"]["downsized_large"]["url"]
        except:
            return

    async def tenor(self, tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
        try:
            return await api_model.arandom(str(tag_name.lower()))
        except:
            return

    async def giphy(self, tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return (await api_model.arandom(
                tag=str(tag_name.lower())
            ))["data"]["images"]["downsized_large"]["url"]
        except:
            return


if __name__ == "__main__":
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        uvloop.install()
    except:
        pass
    MinatoNamikazeBot().run()
