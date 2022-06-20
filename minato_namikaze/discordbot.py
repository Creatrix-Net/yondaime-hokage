import ast
import logging
import random
from collections import Counter, defaultdict, deque
from datetime import timedelta
from typing import Any, List, Optional, Union, TYPE_CHECKING

import aiohttp
import discord
import sentry_sdk
import TenGiphPy
from discord.ext import commands
from discord_together import DiscordTogether
from DiscordDatabase import DiscordDatabase
from DiscordUtils import Embed, ErrorEmbed
from orjson import loads
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

from minato_namikaze.lib import (
    return_all_cogs,
    ChannelAndMessageId,
    Context,
    Database,
    LinksAndVars,
    PaginatedHelpCommand,
    ReactionPersistentView,
    Tokens,
    Webhooks,
    format_dt,
    format_relative,
    post_commands,
    token_get,
)

if TYPE_CHECKING:
    from collections import Counter
    from .cogs.reminder import Reminder

log = logging.getLogger(__name__)


def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
    prefixes = [")", "m!", "minato", "minato "]

    if not message.guild:
        return "m!"

    if bot.local:
        return "!"

    return commands.when_mentioned_or(*prefixes)(bot, message)


class MinatoNamikazeBot(commands.AutoShardedBot):
    user: discord.ClientUser
    command_stats: "Counter[str]"  # type: ignore
    socket_stats: "Counter[str]"  # type: ignore
    gateway_handler: Any
    bot_app_info: discord.AppInfo

    def __init__(self):
        allowed_mentions = discord.AllowedMentions(
            roles=False, everyone=False, users=True
        )
        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
        ).all()
        self.version = str(token_get("BOT_VER"))
        self.local = ast.literal_eval(token_get("LOCAL"))

        self.start_time = discord.utils.utcnow()
        self.github = LinksAndVars.github.value

        self._prev_events = deque(maxlen=10)

        # shard_id: List[datetime.datetime]
        # shows the last attempted IDENTIFYs and RESUMEs
        self.resumes = defaultdict(list)
        self.identifies = defaultdict(list)

        self.spam_control = commands.CooldownMapping.from_cooldown(
            10, 12.0, commands.BucketType.user
        )
        self._auto_spam_count = Counter()

        self.db = DiscordDatabase(self, ChannelAndMessageId.server_id2.value)

        self.uptime = format_relative(self.start_time)
        self.persistent_views_added = False
        self.session = aiohttp.ClientSession()
        self.blacklist: List[Optional[discord.abc.Snowflake]] = []

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

    async def start(self):
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
            await super().start(Tokens.token.value, reconnect=True)
            log.info("Bot started")
        except discord.PrivilegedIntentsRequired:
            log.critical(
                "[Login Failure] You need to enable the server members intent on the Discord Developers Portal."
            )
        except discord.errors.LoginFailure:
            log.critical(
                "[Login Failure] The token initialsed in environment(or .env file) is invalid."
            )
        except KeyboardInterrupt:
            log.critical("The bot is shutting down since force shutdown was initiated.")
        except Exception as e:
            log.critical("An exception occured, %s", e)

    async def on_ready(self):
        self.togetherControl = await DiscordTogether(Tokens.token.value)

        for i in return_all_cogs():
            await self.load_extension(f"minato_namikaze.cogs.{i}")
        try:
            await self.load_extension("jishaku")
        except discord.ext.commands.ExtensionAlreadyLoaded:
            pass
        try:
            await self.tree.sync(guild=discord.Object(id=920536143244709889))
        except (
            discord.HTTPException,
            discord.Forbidden,
            discord.app_commands.MissingApplicationID,
        ):
            pass

        difference = int(
            round(discord.utils.utcnow().timestamp() - self.start_time.timestamp())
        )
        stats = (
            self.get_channel(ChannelAndMessageId.restartlog_channel1.value)
            if not self.local
            else self.get_channel(ChannelAndMessageId.restartlog_channel2.value)
        )
        e = Embed(
            title="Bot Loaded!",
            description=f"Bot ready by **{format_dt(discord.utils.utcnow(), 'R',True)}**, loaded all cogs perfectly! Time to load is {difference} secs :)",
        )
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over Naruto"
            ),
        )
        e.set_thumbnail(url=self.user.avatar.url)

        # if not self.persistent_views_added:
        #     await self.add_persistant_views()

        log.info("Started The Bot")

        try:
            await stats.send(embed=e)
        except:
            pass

        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over Naruto"
            ),
        )
        developer = self.get_cog("Developer")
        if developer is None:
            log.warning("Developer cog is not available")
        else:
            await developer.post()
            log.info("Status Posted")
        await post_commands(self, bool(self.local))
        log.info("Commands Posted")
        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="over Naruto"
            ),
        )

    # async def add_persistant_views(self):
    #     database = await self.db.new(
    #         Database.database_category_name.value,
    #         Database.reaction_roles_channel_name.value,
    #     )
    #     async for message in database._Database__channel.history(limit=None):
    #         cnt = message.content
    #         try:
    #             data = loads(str(cnt))
    #             data.pop("type")
    #             data_keys = list(map(str, list(data.keys())))
    #             data = data[data_keys[0]]
    #             self.add_view(
    #                 ReactionPersistentView(
    #                     reactions_dict=data["reactions"],
    #                     custom_id=data["custom_id"],
    #                     database=database,
    #                 ),
    #                 message_id=int(data_keys[0]),
    #             )
    #             self.persistent_views_added = True
    #         except Exception as e:
    #             log.error(e)
    #             continue
    #     log.info("Persistent views added")

    async def update_blacklist(self):
        database = await self.db.new(
            Database.database_category_name.value,
            Database.user_blacklist_channel_name.value,
        )
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                self.blacklist.append(int(data_keys[0]))
            except Exception as e:
                log.error(e)
                continue
        database = await self.db.new(
            Database.database_category_name.value,
            Database.server_blacklist_channel_name.value,
        )
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                self.blacklist.append(int(data_keys[0]))
                guild = self.get_guild(int(data_keys[0]))
                if guild is not None:
                    channel = await self.get_welcome_channel(guild)
                    embed = ErrorEmbed(title=f"Left {guild.name}")
                    embed.description = f"I have to leave the `{guild.name}` because it was marked as a `blacklist guild` by my developer. For further queries please contact my developer."
                    embed.add_field(
                        name="Developer",
                        value=f"[{self.get_user(self.owner_id)}](https://discord.com/users/{self.owner_id})",
                    )
                    embed.add_field(
                        name="Support Server",
                        value=f"https://discord.gg/{LinksAndVars.invite_code.value}",
                    )
                    await channel.send(embed=embed)
                    await guild.leave()
                    log.info(f"Left guild {guild.id} [Marked as spam]")
            except Exception as e:
                log.error(e)
                continue
        self.blacklist = list(set(self.blacklist))
        log.info("Blacklist Data updated")

    @staticmethod
    async def query_member_named(guild, argument, *, cache=False):
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
            members = await guild.query_members(username, limit=100, cache=cache)
            return discord.utils.get(
                members, name=username, discriminator=discriminator
            )
        else:
            members = await guild.query_members(argument, limit=100, cache=cache)
            return discord.utils.find(lambda m: argument in (m.name, m.nick), members)

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

        members = await guild.query_members(limit=1, user_ids=[member_id], cache=True)
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
                members = await guild.query_members(
                    limit=1, user_ids=needs_resolution, cache=True
                )
                if members:
                    yield members[0]
        elif total_need_resolution <= 100:
            # Only a single resolution call needed here
            resolved = await guild.query_members(
                limit=100, user_ids=needs_resolution, cache=True
            )
            for member in resolved:
                yield member
        else:
            # We need to chunk these in bits of 100...
            for index in range(0, total_need_resolution, 100):
                to_resolve = needs_resolution[index : index + 100]
                members = await guild.query_members(
                    limit=100, user_ids=to_resolve, cache=True
                )
                for member in members:
                    yield member

    async def on_shard_resumed(self, shard_id):
        log.info(f"Shard ID {shard_id} has resumed...")
        self.resumes[shard_id].append(discord.utils.utcnow())

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    @staticmethod
    async def get_bot_inviter(guild: discord.Guild):
        try:
            async for i in guild.audit_logs(
                limit=10, action=discord.AuditLogAction.bot_add
            ):
                return i.user
        except (discord.Forbidden, discord.HTTPException):
            return guild.owner

    @staticmethod
    async def get_welcome_channel(
        guild: discord.Guild,
        inviter_or_guild_owner: Optional[Union[discord.User, discord.Member]] = None,
    ):
        if inviter_or_guild_owner is None:
            inviter_or_guild_owner = guild.owner
        if guild.system_channel is not None:
            return guild.system_channel
        text_channels_list = guild.text_channels
        for i in text_channels_list:
            if i.permissions_for(guild.me).send_messages:
                return i
        return inviter_or_guild_owner

    @property
    def get_admin_invite_link(self):
        return discord.utils.oauth_url(
            self.application_id, 
            permissions=discord.Permissions(administrator=True), 
            redirect_uri="https://minatonamikaze-invites.herokuapp.com/invite", 
            scope=("bot", "applications.commands"), 
            state='cube12345?/Direct From Bot'
        )
    @property
    def get_required_perms_invite_link(self):
        return discord.utils.oauth_url(
            self.application_id, 
            permissions=discord.Permissions(value=1515049189367), 
            redirect_uri="https://minatonamikaze-invites.herokuapp.com/invite", 
            scope=("bot", "applications.commands"), 
            state='cube12345?/Direct From Bot'
        )

    @staticmethod
    def get_random_image_from_tag(tag_name: str) -> Optional[str]:
        tenor_giphy = ["tenor", "giphy"]
        if random.choice(tenor_giphy) == "tenor":
            api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
            try:
                return api_model.random(str(tag_name.lower()))
            except:
                return
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return api_model.random(str(tag_name.lower()))["data"]["images"][
                "downsized_large"
            ]["url"]
        except:
            return

    @staticmethod
    async def get_random_image_from_tag(tag_name: str) -> Optional[str]:
        tenor_giphy = ["tenor", "giphy"]
        if random.choice(tenor_giphy) == "tenor":
            api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
            try:
                return await api_model.arandom(str(tag_name.lower()))
            except:
                return
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return (await api_model.arandom(tag=str(tag_name.lower())))["data"][
                "images"
            ]["downsized_large"]["url"]
        except:
            return

    @staticmethod
    def tenor(tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
        try:
            return api_model.random(str(tag_name.lower()))
        except:
            return

    @staticmethod
    def giphy(tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return api_model.random(str(tag_name.lower()))["data"]["images"][
                "downsized_large"
            ]["url"]
        except:
            return

    @staticmethod
    async def tenor(tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Tenor(token=Tokens.tenor.value)
        try:
            return await api_model.arandom(str(tag_name.lower()))
        except:
            return

    @staticmethod
    async def giphy(tag_name: str) -> Optional[str]:
        api_model = TenGiphPy.Giphy(token=Tokens.giphy.value)
        try:
            return (await api_model.arandom(tag=str(tag_name.lower())))["data"][
                "images"
            ]["downsized_large"]["url"]
        except:
            return

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)

    @staticmethod
    async def log_spammer(ctx, message, retry_after, *, autoblock=False):
        guild_name = getattr(ctx.guild, "name", "No Guild (DMs)")
        guild_id = getattr(ctx.guild, "id", None)
        fmt = "User %s (ID %s) in guild %r (ID %s) spamming, retry_after: %.2fs"
        log.warning(
            fmt, message.author, message.author.id, guild_name, guild_id, retry_after
        )
        if not autoblock:
            return

        embed = discord.Embed(title="Auto-blocked Member", colour=0xDDA453)
        embed.add_field(
            name="Member",
            value=f"{message.author} (ID: {message.author.id})",
            inline=False,
        )
        embed.add_field(
            name="Guild Info", value=f"{guild_name} (ID: {guild_id})", inline=False
        )
        embed.add_field(
            name="Channel Info",
            value=f"{message.channel} (ID: {message.channel.id}",
            inline=False,
        )
        embed.timestamp = discord.utils.utcnow()
        async with aiohttp.ClientSession() as session:
            wh = discord.Webhook.from_url(Webhooks.logs.value, session=session)
            await wh.send(embed=embed)
        return

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is None:
            return

        if ctx.author.id in self.blacklist:
            embed = ErrorEmbed(title="Blacklisted User!")
            embed.description = "You have been `blacklisted` from using my commands. For further queries please contact my developer."
            embed.add_field(
                name="Developer",
                value=f"[{self.get_user(self.owner_id)}](https://discord.com/users/{self.owner_id})",
            )
            embed.add_field(
                name="Support Server",
                value=f"https://discord.gg/{LinksAndVars.invite_code.value}",
            )
            await ctx.send(embed=embed, delete_after=5)
            return

        if ctx.guild is not None and ctx.guild.id in self.blacklist:
            return

        bucket = self.spam_control.get_bucket(message)
        current = message.created_at.timestamp()
        retry_after = bucket.update_rate_limit(current)
        author_id = message.author.id
        if retry_after and author_id != self.owner_id:
            self._auto_spam_count[author_id] += 1
            if self._auto_spam_count[author_id] >= 5:
                await self.add_to_blacklist(author_id)
                del self._auto_spam_count[author_id]
                await self.log_spammer(ctx, message, retry_after, autoblock=True)
            else:
                self.log_spammer(ctx, message, retry_after)
            return
        else:
            self._auto_spam_count.pop(author_id, None)

        try:
            await self.invoke(ctx)
        except:
            pass

    async def add_to_blacklist(self, object_id):
        self.blacklist.append(int(object_id))

    async def on_guild_join(self, guild: discord.Guild):
        if guild.id in self.blacklist:
            channel = await self.get_welcome_channel(guild)
            embed = ErrorEmbed(title=f"Left {guild.name}")
            embed.description = f"I have to leave the `{guild.name}` because it was marked as a `blacklist guild` by my developer. For further queries please contact my developer."
            embed.add_field(
                name="Developer",
                value=f"[{self.get_user(self.owner_id)}](https://discord.com/users/{self.owner_id})",
            )
            embed.add_field(
                name="Support Server",
                value=f"https://discord.gg/{LinksAndVars.invite_code.value}",
            )
            await channel.send(embed=embed)
            await guild.leave()
            log.info(f"Left guild {guild.id} [Marked as spam]")

    async def on_application_command_error(self, response, exception):
        log.error(f"Error; Command: {response.command}, {str(exception)}")

    async def get_context(
        self, origin: Union[discord.Interaction, discord.Message], /, *, cls=Context
    ) -> Context:
        return await super().get_context(origin, cls=cls)

    @property
    def reminder(self) -> "Optional[Reminder]":
        return self.get_cog("Reminder")

    def _clear_gateway_data(self) -> None:
        one_week_ago = discord.utils.utcnow() - timedelta(days=7)
        for shard_id, dates in self.identifies.items():
            to_remove = [index for index, dt in enumerate(dates) if dt < one_week_ago]
            for index in reversed(to_remove):
                del dates[index]

        for shard_id, dates in self.resumes.items():
            to_remove = [index for index, dt in enumerate(dates) if dt < one_week_ago]
            for index in reversed(to_remove):
                del dates[index]

    async def before_identify_hook(self, shard_id: int, *, initial: bool):
        self._clear_gateway_data()
        self.identifies[shard_id].append(discord.utils.utcnow())
        await super().before_identify_hook(shard_id, initial=initial)
