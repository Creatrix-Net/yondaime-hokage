from typing import Optional, Union

import discord


async def get_dm(user: Optional[Union[int, discord.Member]], ctx=None):
    if isinstance(user, int):
        user = ctx.bot.get_user(user)
    return user.dm_channel if user.dm_channel else await user.create_dm()


def get_user(user: Union[int, discord.Member], ctx=None):
    if isinstance(user, int):
        user = ctx.bot.get_user(user)
    return user


def get_roles(role: Union[int, discord.Role], ctx=None):
    if isinstance(role, int):
        role = discord.utils.get(ctx.guild.roles, id=role)
    return role


async def get_bot_inviter(guild: discord.Guild, bot: discord.Client):
    try:
        async for i in guild.audit_logs(limit=1):
            return i.user
    except:
        return guild.owner



async def get_or_fetch_member(guild, member_id):
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

async def resolve_member_ids(guild, member_ids):
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
            members = await guild.query_members(limit=1, user_ids=needs_resolution, cache=True)
            if members:
                yield members[0]
    elif total_need_resolution <= 100:
        # Only a single resolution call needed here
        resolved = await guild.query_members(limit=100, user_ids=needs_resolution, cache=True)
        for member in resolved:
            yield member
    else:
        # We need to chunk these in bits of 100...
        for index in range(0, total_need_resolution, 100):
            to_resolve = needs_resolution[index : index + 100]
            members = await guild.query_members(limit=100, user_ids=to_resolve, cache=True)
            for member in members:
                yield member
