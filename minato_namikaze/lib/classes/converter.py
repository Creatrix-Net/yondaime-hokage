import argparse
import datetime
import re
from typing import Optional, Union
import discord
from discord.ext import commands

from ..functions import ExpiringCache
from ..util.vars import LinksAndVars, ShinobiMatch

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")

time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):

    async def convert(ctx, argument):
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
    return (user.id == ctx.bot.owner_id or user == ctx.guild.owner
            or user.top_role > target.top_role)


class MemberID(commands.Converter):

    async def convert(ctx, argument):
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
                        {
                            "id": argument,
                            "__str__": lambda s: f"Member ID {s.id}"
                        },
                    )()

        if not can_execute_action(ctx, ctx.author, member):
            raise commands.BadArgument(
                "You cannot do this action on this user due to role hierarchy."
            )
        return member


class BannedMember(commands.Converter):

    async def convert(ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(
                    "This member has not been banned before.") from None

        ban_list = await ctx.guild.bans()
        entity = discord.utils.find(lambda u: str(u.user) == argument,
                                    ban_list)

        if entity is None:
            raise commands.BadArgument(
                "This member has not been banned before.")
        return entity


class ActionReason(commands.Converter):

    async def convert(ctx, argument):
        ret = f"{ctx.author} (ID: {ctx.author.id}): {argument}"

        if len(ret) > 512:
            reason_max = 512 - len(ret) + len(argument)
            raise commands.BadArgument(
                f"Reason is too long ({len(argument)}/{reason_max})")
        return ret


def safe_reason_append(base, to_append):
    appended = base + f"({to_append})"
    if len(appended) > 512:
        return base
    return appended


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
            record.get("safe_mention_channel_ids") or [])
        return self


class GiveawayConfig:
    __slots__ = (
        "id", 
        "host", 
        "channel",
        "message", 
        "embed", 
        "role_required", 
        "tasks", 
        "prize", 
        "end_time", 
        "embed_dict"
    )

    @classmethod
    async def from_record(cls, record: discord.Message, bot: commands.Bot):
        self = cls()

        self.id = record.id
        self.channel = record.channel
        
        if len(record.embeds) == 0 or len(record.embeds) > 1:
            raise AttributeError("This is not a giveaway message")

        self.embed = record.embeds[0]
        self.embed_dict = self.embed.to_dict()

        if self.embed_dict.get("fields") is None:
            raise AttributeError("This is not a giveaway message")
        
        if self.embed.description == '\U0001f381 Win a Prize today':
            raise AttributeError("This giveaway has already been ended!")

        role_required = discord.utils.find(lambda a: a["name"].lower() == "Role Required".lower(), self.embed_dict["fields"])
        self.role_required = role_required["value"] if role_required is not None else None
        
        tasks = discord.utils.find(lambda a: a["name"].lower() == "\U0001f3c1 Tasks".lower(), self.embed_dict["fields"])
        self.tasks = tasks["value"] if tasks is not None else None
        
        self.end_time = discord.utils.find(lambda a: a["name"].lower() == "Giveway ends in".lower(), self.embed_dict["fields"])["value"].split('|')[0].strip()
        self.prize = self.embed.description.split('**')[1]
        self.host = self.embed.author
        
        return self


class CooldownByContent(commands.CooldownMapping):

    def _bucket_key(message):
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
            15, 17.0, commands.BucketType.member)
        self.by_user = commands.CooldownMapping.from_cooldown(
            10, 12.0, commands.BucketType.user)
        self.last_join = None
        self.new_user = commands.CooldownMapping.from_cooldown(
            30, 35.0, commands.BucketType.channel)

        # user_id flag mapping (for about 30 minutes)
        self.fast_joiners = ExpiringCache(seconds=1800.0)
        self.hit_and_run = commands.CooldownMapping.from_cooldown(
            10, 12, commands.BucketType.channel)

    @staticmethod
    def is_new(member):
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


class Characters:
    '''The characters model class'''
    __slots__ = [
        'id',
        'name', 
        'images', 
        'emoji',
        'category', 
        'kwargs', 
    ]
    def __init__(self, **kwargs):
        self.name: Optional[str]  = kwargs.get('name')
        self.id: Optional[Union[str,int]] = ''.join(self.name.split()).upper() if self.name is not None else None
        self.images: Optional[list] = kwargs.get('images')
        self.category: Optional[str] = kwargs.get('category')
        self.emoji: Optional[Union[discord.Emoji, discord.PartialEmoji]] = kwargs.get('emoji')
        self.kwargs = kwargs
    
    @property
    def hitpoint(self) -> int:
        category = str(self.category)
        if category.lower() == 'akatsuki':
            return 7
        if category.lower() == 'jinchuruki':
            return 8
        if category.lower() in ('kage', 'special'):
            return 5
        if category.lower() == 'otsutsuki':
            return 10
        if category.lower() == 'special':
            return 6
        else:
            return 3
    
    @property
    def regainpoint(self) -> int:
        category = str(self.category)
        if category.lower() == 'akatsuki':
            return 5
        if category.lower() == 'jinchuruki':
            return 6
        if category.lower() in ('kage', 'special'):
            return 3
        if category.lower() == 'otsutsuki':
            return 7
        if category.lower() == 'special':
            return 4
        else:
            return 1
    
    @property
    def healpoint(self):
        '''These are in percentages'''
        category = str(self.category)
        if category.lower() == 'akatsuki':
            return 50
        if category.lower() == 'jinchuruki':
            return 60
        if category.lower() in ('kage', 'special'):
            return 30
        if category.lower() == 'otsutsuki':
            return 70
        if category.lower() == 'special':
            return 40
        else:
            return 10
    
    @property
    def specialpoint(self):
        '''These are in percentages'''
        category = str(self.category)
        if category.lower() == 'akatsuki':
            return 40
        if category.lower() == 'jinchuruki':
            return 50
        if category.lower() in ('kage', 'special'):
            return 20
        if category.lower() == 'otsutsuki':
            return 60
        if category.lower() == 'special':
            return 30
        else:
            return 10

    @classmethod
    def from_record(cls, record: dict, ctx: commands.Context, name: str):
        self = cls()

        self.name = name.replace("_", " ").title()
        self.images = record['images']
        self.category = record['category']
        self.id = ''.join(self.name.split()).upper() if self.name is not None else None
        self.kwargs = record
        self.emoji = self.return_emoji(url=record['images'][0],category=record['category'],ctx=ctx)
        return self
    
    @staticmethod
    def return_emoji(url:str, category:str, ctx: commands.Context) -> Union[discord.Emoji, discord.PartialEmoji]:
        STRIPPED_STRING_LIST: list = url.lstrip(LinksAndVars.character_data.value.rstrip('img_data.json')+'photo_data/').split('/')
        STRIPPED_STRING_LIST.append(category)
        for i in STRIPPED_STRING_LIST:
            if i.lower() in ShinobiMatch.name_exclusion.value:
                return ctx.get_config_emoji_by_name_or_id(i)
        return discord.PartialEmoji(name='\U0001f5e1')