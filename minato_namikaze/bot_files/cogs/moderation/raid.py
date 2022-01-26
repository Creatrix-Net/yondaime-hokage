import asyncio
from collections import defaultdict

import discord
from discord.ext import commands, tasks
import logging
import datetime
from ...lib import RaidMode, is_mod, cache, format_dt, format_relative

log = logging.getLogger(__name__)

class ModConfig:
    __slots__ = ('raid_mode', 'id', 'bot', 'broadcast_channel_id', 'mention_count',
                 'safe_mention_channel_ids', 'mute_role_id', 'muted_members')

    @classmethod
    async def from_record(cls, record, bot):
        self = cls()

        # the basic configuration
        self.bot = bot
        self.raid_mode = record['raid_mode']
        self.id = record['id']
        self.broadcast_channel_id = record['broadcast_channel']
        return self

    @property
    def broadcast_channel(self):
        guild = self.bot.get_guild(self.id)
        return guild and guild.get_channel(self.broadcast_channel_id)

class CooldownByContent(commands.CooldownMapping):
    def _bucket_key(self, message):
        return (message.channel.id, message.content)

class SpamChecker:
    """This spam checker does a few things.
    1) It checks if a user has spammed more than 10 times in 12 seconds
    2) It checks if the content has been spammed 15 times in 17 seconds.
    3) It checks if new users have spammed 30 times in 35 seconds.
    4) It checks if "fast joiners" have spammed 10 times in 12 seconds.
    The second case is meant to catch alternating spam bots while the first one
    just catches regular singular spam bots.
    From experience these values aren't reached unless someone is actively spamming.
    """
    def __init__(self):
        self.by_content = CooldownByContent.from_cooldown(15, 17.0, commands.BucketType.member)
        self.by_user = commands.CooldownMapping.from_cooldown(10, 12.0, commands.BucketType.user)
        self.last_join = None
        self.new_user = commands.CooldownMapping.from_cooldown(30, 35.0, commands.BucketType.channel)

        # user_id flag mapping (for about 30 minutes)
        self.fast_joiners = cache.ExpiringCache(seconds=1800.0)
        self.hit_and_run = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.channel)

    def is_new(self, member):
        now = discord.utils.utcnow()
        seven_days_ago = now - datetime.timedelta(days=7)
        ninety_days_ago = now - datetime.timedelta(days=90)
        return member.created_at > ninety_days_ago and member.joined_at > seven_days_ago

    def is_spamming(self, message):
        if message.guild is None:
            return False

        current = message.created_at.timestamp()

        if message.author.id in self.fast_joiners:
            bucket = self.hit_and_run.get_bucket(message)
            if bucket.update_rate_limit(current):
                return True

        if self.is_new(message.author):
            new_bucket = self.new_user.get_bucket(message)
            if new_bucket.update_rate_limit(current):
                return True

        user_bucket = self.by_user.get_bucket(message)
        if user_bucket.update_rate_limit(current):
            return True

        content_bucket = self.by_content.get_bucket(message)
        if content_bucket.update_rate_limit(current):
            return True

        return False

    def is_fast_join(self, member):
        joined = member.joined_at or discord.utils.utcnow()
        if self.last_join is None:
            self.last_join = joined
            return False
        is_fast = (joined - self.last_join).total_seconds() <= 2.0
        self.last_join = joined
        if is_fast:
            self.fast_joiners[member.id] = True
        return is_fast


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Some simple moderation commands"
        self._batch_message_lock = self._disable_lock = asyncio.Lock(loop=bot.loop)
        self._spam_check = defaultdict(SpamChecker)
        self.message_batches = defaultdict(list)
        self.bulk_send_messages.start()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="discord_certified_moderator",id=922030031146995733)
    
    @tasks.loop(seconds=10.0)
    async def bulk_send_messages(self):
        async with self._batch_message_lock:
            for ((guild_id, channel_id), messages) in self.message_batches.items():
                guild = self.bot.get_guild(guild_id)
                channel = guild and guild.get_channel(channel_id)
                if channel is None:
                    continue

                paginator = commands.Paginator(suffix='', prefix='')
                for message in messages:
                    paginator.add_line(message)

                for page in paginator.pages:
                    try:
                        await channel.send(page)
                    except discord.HTTPException:
                        pass

            self.message_batches.clear()
    
    @cache()
    async def get_guild_config(self, guild_id):
        query = """SELECT * FROM guild_mod_config WHERE id=$1;"""
        async with self.bot.pool.acquire(timeout=300.0) as con:
            record = await con.fetchrow(query, guild_id)
            if record is not None:
                return await ModConfig.from_record(record, self.bot)
            return None
    
    async def check_raid(self, config, guild_id, member, message):
        if config.raid_mode != RaidMode.strict.value:
            return

        checker = self._spam_check[guild_id]
        if not checker.is_spamming(message):
            return

        try:
            await member.ban(reason='Auto-ban from spam (strict raid mode ban)')
        except discord.HTTPException:
            log.info(f'[Raid Mode] Failed to ban {member} (ID: {member.id}) from server {member.guild} via strict mode.')
        else:
            log.info(f'[Raid Mode] Banned {member} (ID: {member.id}) from server {member.guild} via strict mode.')

    @tasks.loop(seconds=10.0)
    async def bulk_send_messages(self):
        async with self._batch_message_lock:
            for ((guild_id, channel_id),
                 messages) in self.message_batches.items():
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

    @commands.Cog.listener()
    async def on_message(self, message):
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
        config = await self.get_guild_config(guild_id)
        if config is None:
            return

        # check for raid mode stuff
        await self.check_raid(config, guild_id, author, message)

        # auto-ban tracking for mention spams begin here
        if len(message.mentions) <= 3:
            return

        if not config.mention_count:
            return

        # check if it meets the thresholds required
        mention_count = sum(not m.bot and m.id != author.id
                            for m in message.mentions)
        if mention_count < config.mention_count:
            return

        if message.channel.id in config.safe_mention_channel_ids:
            return

        try:
            await author.ban(
                reason=f"Spamming mentions ({mention_count} mentions)")
        except Exception as e:
            log.info(
                f"Failed to autoban member {author} (ID: {author.id}) in guild ID {guild_id}"
            )
        else:
            to_send = f"Banned {author} (ID: {author.id}) for spamming {mention_count} mentions."
            async with self._batch_message_lock:
                self.message_batches[(guild_id,
                                      message.channel.id)].append(to_send)

            log.info(
                f"Member {author} (ID: {author.id}) has been autobanned from guild ID {guild_id}"
            )

    @commands.Cog.listener()
    async def on_member_join(self, member):
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
        title = 'Member Joined'
        if checker.is_fast_join(member):
            colour = 0xdd5f53 # red
            if is_new:
                title = 'Member Joined (Very New Member)'
        else:
            colour = 0x53dda4 # green

            if is_new:
                colour = 0xdda453 # yellow
                title = 'Member Joined (Very New Member)'

        e = discord.Embed(title=title, colour=colour)
        e.timestamp = now
        e.set_author(name=str(member), icon_url=member.display_avatar.url)
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Joined', value=format_dt(member.joined_at, "F"))
        e.add_field(name='Created', value=format_relative(member.created_at), inline=False)

        if config.broadcast_channel:
            try:
                await config.broadcast_channel.send(embed=e)
            except discord.Forbidden:
                async with self._disable_lock:
                    await self.disable_raid_mode(guild_id)

    @commands.group(aliases=['raids'], invoke_without_command=True)
    @is_mod()
    async def raid(self, ctx):
        """Controls raid mode on the server.
        Calling this command with no arguments will show the current raid
        mode information.
        You must have Manage Server permissions to use this command or
        its subcommands.
        """

        query = "SELECT raid_mode, broadcast_channel FROM guild_mod_config WHERE id=$1;"

        row = await ctx.db.fetchrow(query, ctx.guild.id)
        if row is None:
            fmt = 'Raid Mode: off\nBroadcast Channel: None'
        else:
            ch = f'<#{row[1]}>' if row[1] else None
            mode = RaidMode(row[0]) if row[0] is not None else RaidMode.off
            fmt = f'Raid Mode: {mode}\nBroadcast Channel: {ch}'

        await ctx.send(fmt)

    @raid.command(name='on', aliases=['enable', 'enabled'])
    @is_mod()
    async def raid_on(self, ctx, *, channel: discord.TextChannel = None):
        """
        Enables basic raid mode on the server.
        When enabled, server verification level is set to table flip
        levels and allows the bot to broadcast new members joining
        to a specified channel.
        If no channel is given, then the bot will broadcast join
        messages on the channel this command was used in.
        """

        channel = channel or ctx.channel

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.high)
        except discord.HTTPException:
            await ctx.send('\N{WARNING SIGN} Could not set verification level.')

        query = """INSERT INTO guild_mod_config (id, raid_mode, broadcast_channel)
                   VALUES ($1, $2, $3) ON CONFLICT (id)
                   DO UPDATE SET
                        raid_mode = EXCLUDED.raid_mode,
                        broadcast_channel = EXCLUDED.broadcast_channel;
                """

        await ctx.db.execute(query, ctx.guild.id, RaidMode.on.value, channel.id)
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(f'Raid mode enabled. Broadcasting join messages to {channel.mention}.')

    async def disable_raid_mode(self, guild_id):
        query = """INSERT INTO guild_mod_config (id, raid_mode, broadcast_channel)
                   VALUES ($1, $2, NULL) ON CONFLICT (id)
                   DO UPDATE SET
                        raid_mode = EXCLUDED.raid_mode,
                        broadcast_channel = NULL;
                """

        await self.bot.pool.execute(query, guild_id, RaidMode.off.value)
        self._spam_check.pop(guild_id, None)
        self.get_guild_config.invalidate(self, guild_id)

    @raid.command(name='off', aliases=['disable', 'disabled'])
    @is_mod()
    async def raid_off(self, ctx):
        """Disables raid mode on the server.
        When disabled, the server verification levels are set
        back to Low levels and the bot will stop broadcasting
        join messages.
        """

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.low)
        except discord.HTTPException:
            await ctx.send('\N{WARNING SIGN} Could not set verification level.')

        await self.disable_raid_mode(ctx.guild.id)
        await ctx.send('Raid mode disabled. No longer broadcasting join messages.')

    @raid.command(name='strict')
    @is_mod()
    async def raid_strict(self, ctx, *, channel: discord.TextChannel = None):
        """
        Enables strict raid mode on the server.
        Strict mode is similar to regular enabled raid mode, with the added
        benefit of auto-banning members that are spamming. The threshold for
        spamming depends on a per-content basis and also on a per-user basis
        of 15 messages per 17 seconds.
        If this is considered too strict, it is recommended to fall back to regular
        raid mode.
        """
        channel = channel or ctx.channel

        perms = ctx.me.guild_permissions
        if not (perms.kick_members and perms.ban_members):
            return await ctx.send('\N{NO ENTRY SIGN} I do not have permissions to kick and ban members.')

        try:
            await ctx.guild.edit(verification_level=discord.VerificationLevel.high)
        except discord.HTTPException:
            await ctx.send('\N{WARNING SIGN} Could not set verification level.')

        query = """INSERT INTO guild_mod_config (id, raid_mode, broadcast_channel)
                   VALUES ($1, $2, $3) ON CONFLICT (id)
                   DO UPDATE SET
                        raid_mode = EXCLUDED.raid_mode,
                        broadcast_channel = EXCLUDED.broadcast_channel;
                """

        await ctx.db.execute(query, ctx.guild.id, RaidMode.strict.value, channel.id)
        self.get_guild_config.invalidate(self, ctx.guild.id)
        await ctx.send(f'Raid mode enabled strictly. Broadcasting join messages to {channel.mention}.')


def setup(bot):
    bot.add_cog(AntiRaid(bot))
