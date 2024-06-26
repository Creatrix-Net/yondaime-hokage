from __future__ import annotations

import ast
import copy
from datetime import timezone

import discord
from discord.ext import commands
from psutil._common import bytes2human

from ..util.utility import return_matching_emoji


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


async def copy_context_with(
    ctx: commands.Context, *, author=None, channel=None, **kwargs
):

    alt_message: discord.Message = copy.copy(ctx.message)
    alt_message._update(kwargs)  # pylint: disable=protected-access

    if author is not None:
        alt_message.author = author
    if channel is not None:
        alt_message.channel = channel

    # obtain and return a context of the same type
    return await ctx.bot.get_context(alt_message, cls=type(ctx))


# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# Certain permissions signify if the person is a moderator (Manage Server) or an
# admin (Administrator). Having these signify certain bypasses.
# Of course, the owner will always be able to execute commands.
async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)

    return commands.check(pred)


async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_guild_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, check=check)

    return commands.check(pred)


def is_mod():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {"manage_guild": True})

    return commands.check(pred)


def is_admin():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {"administrator": True})

    return commands.check(pred)


def mod_or_permissions(**perms):
    perms["manage_guild"] = True

    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def admin_or_permissions(**perms):
    perms["administrator"] = True

    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return commands.check(predicate)


async def serverinfo(
    guild: discord.Guild,
    author: discord.Member,
    bot,
) -> discord.Embed:
    levels = {
        "None - No criteria set.": discord.VerificationLevel.none,
        "Low - Member must have a verified email on their Discord account.": discord.VerificationLevel.low,
        "Medium - Member must have a verified email and be registered on Discord for more than five minutes.": discord.VerificationLevel.medium,
        "High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the guild itself for more than ten minutes.": discord.VerificationLevel.high,
        "Extreme - Member must have a verified phone on their Discord account.": discord.VerificationLevel.highest,
    }
    filters = {
        "Disabled - The guild does not have the content filter enabled.": discord.ContentFilter.disabled,
        "No Role - The guild has the content filter enabled for members without a role.": discord.ContentFilter.no_role,
        "All Members - The guild has the content filter enabled for every member.": discord.ContentFilter.all_members,
    }
    nsfw_level = {
        discord.NSFWLevel.default: "The guild has not been categorised yet.",
        discord.NSFWLevel.explicit: "The guild contains NSFW content.",
        discord.NSFWLevel.safe: "The guild does not contain any NSFW content.",
        discord.NSFWLevel.age_restricted: "The guild may contain NSFW content.",
    }
    find_bots = sum(1 for member in guild.members if member.bot)

    embed = discord.Embed(
        title=f"Server: __{guild.name}__ Info",
        color=author.top_role.color,
        description=f":id: Server ID: `{guild.id}`",
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.with_format("png").url)

    verif_lvl = "None"
    for text, dvl in levels.items():
        if dvl is guild.verification_level:
            verif_lvl = text
    for response, filt in filters.items():
        if filt is guild.explicit_content_filter:
            content_filter = response
    embed.add_field(name=":crown: Owner", value=guild.owner)
    embed.add_field(name="Max Bitrate", value=str(guild.bitrate_limit / 1000) + "kbps")
    embed.add_field(name="File Size", value=bytes2human(guild.filesize_limit))
    embed.add_field(name=":heavy_check_mark: Verification Level", value=verif_lvl)
    embed.add_field(name=":warning: Content Filter", value=content_filter)
    embed.add_field(name=":busts_in_silhouette: Members", value=guild.member_count)
    embed.add_field(name=":robot: Bots", value=find_bots)
    embed.add_field(name=":performing_arts: Roles", value=f"{len(guild.roles)}")
    embed.add_field(
        name=":star: Emotes",
        value=f"{len(guild.emojis)}/{guild.emoji_limit}",
    )
    embed.add_field(
        name=":calendar: Created On",
        value=f"<t:{round(guild.created_at.timestamp())}:D>",
    )
    embed.add_field(
        name=":level_slider: NSFW Level",
        value=nsfw_level[guild.nsfw_level],
    )
    embed.add_field(
        name=":key: 2FA",
        value="Enabled" if bool(guild.mfa_level.value) else "Disabled",
    )
    embed.add_field(
        name=":bell: Notifications",
        value=(
            "All Messages "
            if guild.default_notifications == discord.NotificationLevel.all_messages
            else "Disabled"
        ),
    )
    embed.add_field(name="Categories", value=len(guild.categories))
    embed.add_field(
        name=f"{str(await return_matching_emoji(bot, 'text_channel'))} Text Channels",
        value=len(guild.text_channels),
    )
    embed.add_field(
        name=f"{str(await return_matching_emoji(bot, 'voice_channel'))} Voice Channels",
        value=len(guild.voice_channels),
    )
    embed.add_field(
        name=f"{str(await return_matching_emoji(bot, 'stage_channel'))} Stage Channels",
        value=len(guild.stage_channels),
    )
    if len(guild.features) != 0:
        embed.add_field(
            name="Features",
            value="".join(f"- {i}\n" for i in guild.features),
            inline=False,
        )
    return embed


async def userinfo(user: discord.Member, guild: discord.Guild, bot) -> discord.Embed:
    dt = user.joined_at
    dt1 = user.created_at
    unix_ts_utc = dt.replace(tzinfo=timezone.utc).timestamp()
    unix_ts_utc1 = dt1.replace(tzinfo=timezone.utc).timestamp()
    user_c_converter = int(unix_ts_utc1)
    user_j_converter = int(unix_ts_utc)

    since_created = f"<t:{user_c_converter}:R>"
    if user.joined_at is not None:
        since_joined = f"<t:{user_j_converter}:R>"
        user_joined = f"<t:{user_j_converter}:D>"
    else:
        since_joined = "?"
        user_joined = "Unknown"
    user_created = f"<t:{user_c_converter}:D>"
    created_on = ("{} - ({})").format(since_created, user_created)
    joined_on = ("{} - ({})\n").format(since_joined, user_joined)

    # to get status of user with emoji
    status = ""
    s = user.status
    if s == discord.Status.online:
        status += str(await return_matching_emoji(name="online", bot=bot))
    if s == discord.Status.offline:
        status += str(await return_matching_emoji(name="offline", bot=bot))
    if s == discord.Status.idle:
        status += str(await return_matching_emoji(name="idle", bot=bot))
    if s == discord.Status.dnd:
        status += str(await return_matching_emoji(name="dnd", bot=bot))

    show_roles = (
        ", ".join(
            [
                f"<@&{x.id}>"
                for x in sorted(user.roles, key=lambda x: x.position, reverse=True)
                if x.id != guild.default_role.id
            ],
        )
        if len(user.roles) > 1
        else "None"
    )

    embed = discord.Embed(
        title=f"{status} {user.display_name}'s Info.",
        colour=user.top_role.colour.value,
        description=f":id: User ID: `{user.id}`",
    )
    embed.set_thumbnail(url=user.avatar.url)

    embed.add_field(name=":small_blue_diamond: User", value=user, inline=True)
    if user.nick:
        embed.add_field(
            name=":small_blue_diamond: Nickname",
            value=user.nick,
            inline=True,
        )
    embed.add_field(
        name="**__User info__**",
        value=(":date: Joined On {}").format(joined_on),
        inline=False,
    )
    embed.add_field(
        name="**__Member Info__**",
        value=(":date: Created On: {}").format(created_on),
        inline=True,
    )
    embed.add_field(name=":small_orange_diamond: Roles", value=show_roles, inline=False)
    if user.banner:
        embed.set_image(url=user.banner)
    return embed
