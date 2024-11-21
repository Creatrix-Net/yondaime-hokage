from __future__ import annotations

import asyncio
import datetime
import logging
from collections import defaultdict
from json.decoder import JSONDecodeError
from typing import Literal
from typing import TYPE_CHECKING

import discord
import num2words
from discord.ext import commands
from discord.ext import tasks
from orjson import loads
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import JSONB
from sqlalchemy import SmallInteger
from sqlalchemy import String

from minato_namikaze.lib import AntiRaidConfig
from minato_namikaze.lib import Base
from minato_namikaze.lib import cache
from minato_namikaze.lib import format_dt
from minato_namikaze.lib import format_relative
from minato_namikaze.lib import has_permissions
from minato_namikaze.lib import InviteTracker
from minato_namikaze.lib import is_mod
from minato_namikaze.lib import MemberID
from minato_namikaze.lib import MentionSpamConfig
from minato_namikaze.lib import RaidMode
from minato_namikaze.lib import SpamChecker

if TYPE_CHECKING:
    from lib import Context

    from minato_namikaze import MinatoNamikazeBot

log = logging.getLogger(__name__)


class Raid(Base):
    __tablename__ = "raid"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, index=True, primary_key=True)
    guild_id = Column(BigInteger, index=True)
    raid_mode = Column(SmallInteger, index=True, nullable=False)
    expires = Column(DateTime, index=True)
    created = Column(DateTime, default="now() at time zone 'utc'", nullable=False)
    event = Column(String, nullable=False)
    extra = Column(JSONB, nullable=True)


class AntiRaid(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Antiraid system commands to use"
        self._batch_message_lock = self._disable_lock = asyncio.Lock()
        self.autoban_threshold = 3
        self._spam_check = defaultdict(SpamChecker)
        self.message_batches = defaultdict(list)
        self.tracker = InviteTracker(bot)
        self.bulk_send_messages.start()
        self.cleanup.start()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(
            name="discord_certified_moderator",
            id=922030031146995733,
        )

    # async def database_class_antiraid(self):
    #     return await self.bot.db.new(
    #         Database.database_category_name.value,
    #         Database.antiraid_channel_name.value,
    #     )

    # async def database_class_mentionspam(self):
    #     return await self.bot.db.new(
    #         Database.database_category_name.value,
    #         Database.mentionspam_channel_name.value,
    #     )

    @tasks.loop(hours=1, reconnect=True)
    async def cleanup(self):
        database = await self.database_class_antiraid()
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                try:
                    await commands.GuildConverter().convert(
                        await self.bot.get_context(message),
                        str(data_keys[0]),
                    )
                except (commands.CommandError, commands.BadArgument):
                    if not self.bot.local:
                        await message.delete()
            except JSONDecodeError:
                if not self.bot.local:
                    await message.delete()

        database = await self.database_class_mentionspam()
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                try:
                    await commands.GuildConverter().convert(
                        await self.bot.get_context(message),
                        str(data_keys[0]),
                    )
                except (commands.CommandError, commands.BadArgument):
                    await message.delete()
            except JSONDecodeError:
                await message.delete()

    async def add_and_check_data(
        self,
        dict_to_add: dict,
        ctx: Context,
        type_database: Literal["antiraid", "mentionspam"] | None = "antiraid",
    ) -> None:
        if type_database.lower() == "antiraid":
            database = await self.database_class_antiraid()
        else:
            database = await self.database_class_mentionspam()
        guild_dict = await database.get(ctx.guild.id)
        if guild_dict is None:
            await database.set(ctx.guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await database.set(ctx.guild.id, guild_dict)
        return

    @tasks.loop(seconds=10.0)
    async def bulk_send_messages(self):
        async with self._batch_message_lock:
            for (guild_id, channel_id), messages in self.message_batches.items():
                guild = self.bot.get_guild(guild_id)
                channel = guild and guild.get_channel(channel_id)
                if channel is None:
                    continue

                paginator = commands.Paginator(suffix="", prefix="")
                for message in messages:
                    paginator.add_line(message)

                for page in paginator.pages:
                    try:
                        await channel.send(page)
                    except discord.HTTPException:
                        pass

            self.message_batches.clear()

    @cache()
    async def get_guild_config(
        self,
        guild_id: int,
        type_database: Literal["antiraid", "mentionspam"] | None = "antiraid",
    ):
        if type_database.lower() == "antiraid":
            database = await self.database_class_antiraid()
        else:
            database = await self.database_class_mentionspam()
        record = await database.get(guild_id)
        if record is not None:
            record.update({"id": guild_id})
            if type_database.lower() == "antiraid":
                return await AntiRaidConfig.from_record(record, self.bot)
            else:
                return await MentionSpamConfig.from_record(record, self.bot)
        return None

    async def check_raid(self, config, guild_id, member, message):
        if config.raid_mode != RaidMode.strict.value:
            return

        checker = self._spam_check[guild_id]
        if not checker.is_spamming(message):
            return

        try:
            await member.ban(reason="Auto-ban from spam (strict raid mode ban)")
        except discord.HTTPException:
            log.info(
                f"[Raid Mode] Failed to ban {member} (ID: {member.id}) from server {member.guild} via strict mode.",
            )
        else:
            log.info(
                f"[Raid Mode] Banned {member} (ID: {member.id}) from server {member.guild} via strict mode.",
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        author = message.author
        if author.id in (self.bot.user.id, self.bot.owner_id):
            return

        if message.guild is None:
            return

        if not isinstance(author, discord.Member):
            return

        if author.bot:
            return

        # we're going to ignore members with manage messages
        if author.guild_permissions.manage_messages:
            return

        guild_id = message.guild.id
        config_antiraid = await self.get_guild_config(guild_id)
        config_mentionspam = await self.get_guild_config(guild_id, "mentionspam")
        if config_antiraid is None and config_mentionspam is None:
            return

        # check for raid mode stuff
        await self.check_raid(config_antiraid, guild_id, author, message)

        # auto-ban tracking for mention spams begin here
        if len(message.mentions) <= self.autoban_threshold:
            return

        if config_mentionspam is None:
            return

        if not config_mentionspam.mention_count:
            return

        # check if it meets the thresholds required
        mention_count = sum(not m.bot and m.id != author.id for m in message.mentions)
        if mention_count < config_mentionspam.mention_count:
            return

        if message.channel.id in config_mentionspam.safe_mention_channel_ids:
            return

        try:
            await author.ban(reason=f"Spamming mentions ({mention_count} mentions)")
        except Exception as e:
            log.info(
                f"Failed to autoban member {author} (ID: {author.id}) in guild ID {guild_id}",
            )
        else:
            to_send = f"Banned {author} (ID: {author.id}) for spamming {mention_count} mentions."
            async with self._batch_message_lock:
                self.message_batches[(guild_id, message.channel.id)].append(to_send)

            log.info(
                f"Member {author} (ID: {author.id}) has been autobanned from guild ID {guild_id}",
            )

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member | MemberID | discord.User,
    ):
        guild_id = member.guild.id
        config = await self.get_guild_config(guild_id)
        if config is None:
            return

        if not config.raid_mode:
            return

        now = discord.utils.utcnow()

        is_new = member.created_at > (now - datetime.timedelta(days=7))
        checker = self._spam_check[guild_id]

        # Do the broadcasted message to the channel
        title = "Member Joined"
        if checker.is_fast_join(member):
            colour = 0xDD5F53  # red
            if is_new:
                title = "Member Joined (Very New Member)"
        else:
            colour = discord.Color.green()  # green

            if is_new:
                colour = discord.Color.yellow()  # yellow
                title = "Member Joined (Very New Member)"

        e = discord.Embed(title=title, colour=colour)
        e.timestamp = now
        e.set_author(name=str(member), icon_url=member.display_avatar.url)
        e.add_field(name="ID", value=member.id)
        e.add_field(name="Joined", value=format_dt(member.joined_at, "F"))
        e.add_field(
            name="Created",
            value=format_relative(member.created_at),
            inline=False,
        )
        try:
            e.add_field(
                name="Inviter",
                value=str((await self.tracker.fetch_inviter(member)).inviter),
            )
            e.add_field(
                name="Invite Code",
                value=str((await self.tracker.fetch_inviter(member)).code),
            )
            e.add_field(
                name="Invite Code Uses",
                value=str((await self.tracker.fetch_inviter(member)).uses),
            )
        except AttributeError:
            pass

        if config.broadcast_channel:
            try:
                await config.broadcast_channel.send(embed=e)
            except discord.Forbidden:
                async with self._disable_lock:
                    await self.disable_raid_mode(guild_id)

    @commands.group(aliases=["raids", "antiraid"], invoke_without_command=True)
    @is_mod()
    async def raid(self, ctx: Context):
        """Controls raid mode on the server.
        Calling this command with no arguments will show the current raid
        mode information.
        You must have Manage Server permissions to use this command or
        its subcommands.
        """

        database = await self.database_class_antiraid()
        guild_dict = await database.get(ctx.guild.id)

        if guild_dict is None:
            fmt = "Raid Mode: off\nBroadcast Channel: None"
        else:
            ch = f"<#{guild_dict['broadcast_channel']}>" if guild_dict["broadcast_channel"] else None
            mode = RaidMode(guild_dict["raid_mode"]) if guild_dict["raid_mode"] is not None else RaidMode.off
            fmt = f"Raid Mode: {mode.name.capitalize()}\nBroadcast Channel: {ch}"

        await ctx.send(fmt)

    @raid.command(name="on", aliases=["enable", "enabled"])
    @is_mod()
    async def raid_on(self, ctx: Context, *, channel: discord.TextChannel = None):
        """
        Enables basic raid mode on the server.
        When enabled, server verification level is set to table flip
        levels and allows the bot to broadcast new members joining
        to a specified channel.
        If no channel is given, then the bot will broadcast join
        messages on the channel this command was used in.
        """

        if not await ctx.prompt(
            "Are you sure that you want to **turn on the raid mode** for the guild?",
            author_id=ctx.author.id,
        ):
            return

        channel = channel or ctx.channel

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.medium)
        except discord.HTTPException:
            await ctx.send("\N{WARNING SIGN} Could not set verification level.")

        update_dict = {"raid_mode": RaidMode.on.value, "broadcast_channel": channel.id}
        await self.add_and_check_data(dict_to_add=update_dict, ctx=ctx)

        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(
            f"Raid mode enabled. Broadcasting join messages to {channel.mention}.",
        )

    async def disable_raid_mode(self, guild_id):
        database = await self.database_class_antiraid()
        await database.delete(guild_id)
        self._spam_check.pop(guild_id, None)
        self.get_guild_config.invalidate(self, guild_id)

    @raid.command(name="off", aliases=["disable", "disabled"])
    @is_mod()
    async def raid_off(self, ctx: Context):
        """Disables raid mode on the server.
        When disabled, the server verification levels are set
        back to Low levels and the bot will stop broadcasting
        join messages.
        """

        if not await ctx.prompt(
            "Are you sure that you want to **turn off the raid mode** for the guild?",
            author_id=ctx.author.id,
        ):
            return

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.low)
        except discord.HTTPException:
            await ctx.send("\N{WARNING SIGN} Could not set verification level.")

        await self.disable_raid_mode(ctx.guild.id)
        await ctx.send("Raid mode disabled. No longer broadcasting join messages.")

    @raid.command(name="strict")
    @is_mod()
    async def raid_strict(self, ctx: Context, *, channel: discord.TextChannel = None):
        """
        Enables strict raid mode on the server.
        Strict mode is similar to regular enabled raid mode, with the added
        benefit of auto-banning members that are spamming. The threshold for
        spamming depends on a per-content basis and also on a per-user basis
        of 15 messages per 17 seconds.
        If this is considered too strict, it is recommended to fall back to regular
        raid mode.
        """
        if not await ctx.prompt(
            "Are you sure that you want to set **raid mode to strict** for the guild?",
            author_id=ctx.author.id,
        ):
            return

        channel = channel or ctx.channel

        perms = ctx.me.guild_permissions
        if not (perms.kick_members and perms.ban_members):
            return await ctx.send(
                "\N{NO ENTRY SIGN} I do not have permissions to kick and ban members.",
            )

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.high)
        except discord.HTTPException:
            await ctx.send("\N{WARNING SIGN} Could not set verification level.")

        update_dict = {
            "raid_mode": RaidMode.strict.value,
            "broadcast_channel": channel.id,
        }
        await self.add_and_check_data(dict_to_add=update_dict, ctx=ctx)
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(
            f"Raid mode enabled strictly. Broadcasting join messages to {channel.mention}.",
        )

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def mentionspam(self, ctx: Context, count: int | None = None):
        """Enables auto-banning accounts that spam mentions.
        If a message contains `count` or more mentions then the
        bot will automatically attempt to auto-ban the member.
        The `count` must be greater than 3.
        If the `count` is 0 then this is disabled (also deletes the data from database).
        This only applies for user mentions. Everyone or Role
        mentions are not included.
        To use this command you must have the Ban Members permission.
        """

        database = await self.database_class_mentionspam()
        if count is None:
            guild_dict = await database.get(ctx.guild.id)
            if guild_dict is None:
                return await ctx.send(
                    "This server has not set up mention spam banning.",
                )

            ignores = ", ".join(f"<#{e}>" for e in guild_dict.get("safe_mention_channel_ids", [])) or "None"
            return await ctx.send(
                f'- Threshold: {guild_dict["mention_count"]} mentions\n- Ignored Channels: {ignores}',
            )

        if count == 0:
            if not await ctx.prompt(
                "Are you sure that you want to **disable autoban for the spam mention** for the guild?",
                author_id=ctx.author.id,
            ):
                return
            await database.delete(ctx.guild.id)
            self.get_guild_config.invalidate(self, ctx.guild.id)
            return await ctx.send("Auto-banning members has been disabled.")

        if count <= self.autoban_threshold:
            await ctx.send(
                f"\N{NO ENTRY SIGN} Auto-ban threshold must be greater than `{' '.join(num2words.num2words(self.autoban_threshold).split('-'))}`.",
            )
            return

        if not await ctx.prompt(
            f"Are you sure that you want to **autoban for the spam mention of more than {count}** for the guild?",
            author_id=ctx.author.id,
        ):
            return

        await self.add_and_check_data(
            dict_to_add={"mention_count": count},
            ctx=ctx,
            type_database="mentionspam",
        )
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(
            f"Now auto-banning members that mention more than {count} users.",
        )

    @mentionspam.command(name="ignore", aliases=["bypass"])
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def mentionspam_ignore(self, ctx: Context, *channels: discord.TextChannel):
        """Specifies what channels ignore mentionspam auto-bans.
        If a channel is given then that channel will no longer be protected
        by auto-banning from mention spammers.
        To use this command you must have the Ban Members permission.
        """

        if not await ctx.prompt(
            f"Are you sure that you want to **ignore {len(channels)} channel(s) for the spam mention**, for the guild?",
            author_id=ctx.author.id,
        ):
            return

        if len(channels) == 0:
            return await ctx.send("Missing channels to ignore.")

        if len(channels) > 50:
            return await ctx.send(
                "Sorry you cannot add more than 50 channels to the ignore list",
            )

        channel_ids = [c.id for c in channels]
        dict_update = {"safe_mention_channel_ids": channel_ids}
        await self.add_and_check_data(
            dict_to_add=dict_update,
            ctx=ctx,
            type_database="mentionspam",
        )
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(
            f'Mentions are now ignored on {", ".join(c.mention for c in channels)}.',
        )

    @mentionspam.command(name="unignore", aliases=["protect"])
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def mentionspam_unignore(
        self,
        ctx: Context,
        *channels: discord.TextChannel,
    ):
        """Specifies what channels to take off the ignore list.
        To use this command you must have the Ban Members permission.
        """

        if not await ctx.prompt(
            f"Are you sure that you want to **remove {len(channels)} channel(s) from the ignore list**, for the guild?",
            author_id=ctx.author.id,
        ):
            return

        if len(channels) == 0:
            return await ctx.send("Missing channels to protect.")

        database = await self.database_class_mentionspam()
        guild_dict = await database.get(ctx.guild.id)
        if guild_dict is None:
            return

        ignore_list = guild_dict.get("safe_mention_channel_ids")
        if ignore_list is None:
            return

        for i in channels:
            try:
                ignore_list.remove(i.id)
            except:
                pass

        guild_dict.update({"safe_mention_channel_ids": ignore_list})
        await database.set(ctx.guild.id, guild_dict)
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send("Updated mentionspam ignore list.")


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(AntiRaid(bot))
