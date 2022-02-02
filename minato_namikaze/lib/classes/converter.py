import argparse
import datetime
import re

import discord
from discord.ext import commands

from ..functions import ExpiringCache

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")

time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)


def can_execute_action(ctx, user, target):
    return (
        user.id == ctx.bot.owner_id
        or user == ctx.guild.owner
        or user.top_role > target.top_role
    )


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            member = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                argument = int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(
                    f"{argument} is not a valid member or member ID."
                ) from None
            else:
                member = await ctx.bot.get_or_fetch_member(ctx.guild, argument)
                if member is None:
                    # hackban case
                    return type(
                        "_Hackban",
                        (),
                        {"id": argument, "__str__": lambda s: f"Member ID {s.id}"},
                    )()

        if not can_execute_action(ctx, ctx.author, member):
            raise commands.BadArgument(
                "You cannot do this action on this user due to role hierarchy."
            )
        return member


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(
                    "This member has not been banned before."
                ) from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(
            lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument(
                "This member has not been banned before.")
        return entity


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = f"{ctx.author} (ID: {ctx.author.id}): {argument}"

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(
                f"Reason is too long ({len(argument)}/{reason_max})"
            )
        return ret


def safe_reason_append(base, to_append):
    appended = base + f"({to_append})"
    if len(appended) > 512:
        return base
    return appended


def can_execute_action(ctx, user, target):
    return (
        user.id == ctx.bot.owner_id
        or user == ctx.guild.owner
        or user.top_role > target.top_role
    )


class AntiRaidConfig:
    __slots__ = ("raid_mode", "id", "bot", "broadcast_channel_id")

    @classmethod
    async def from_record(cls, record, bot):
        self = cls()

        # the basic configuration
        self.bot = bot
        self.raid_mode = record["raid_mode"]
        self.id = record["id"]
        self.broadcast_channel_id = record["broadcast_channel"]
        return self

    @property
    def broadcast_channel(self):
        guild = self.bot.get_guild(self.id)
        return guild and guild.get_channel(self.broadcast_channel_id)


class MentionSpamConfig:
    __slots__ = ("id", "bot", "mention_count", "safe_mention_channel_ids")

    @classmethod
    async def from_record(cls, record, bot):
        self = cls()

        # the basic configuration
        self.bot = bot
        self.id = record["id"]
        self.mention_count = record.get("mention_count")
        self.safe_mention_channel_ids = set(
            record.get("safe_mention_channel_ids") or []
        )
        return self


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
        self.by_content = CooldownByContent.from_cooldown(
            15, 17.0, commands.BucketType.member
        )
        self.by_user = commands.CooldownMapping.from_cooldown(
            10, 12.0, commands.BucketType.user
        )
        self.last_join = None
        self.new_user = commands.CooldownMapping.from_cooldown(
            30, 35.0, commands.BucketType.channel
        )

        # user_id flag mapping (for about 30 minutes)
        self.fast_joiners = ExpiringCache(seconds=1800.0)
        self.hit_and_run = commands.CooldownMapping.from_cooldown(
            10, 12, commands.BucketType.channel
        )

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
