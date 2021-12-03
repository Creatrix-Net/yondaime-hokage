import random
from functools import cache, cached_property, lru_cache, wraps
from typing import Optional, Union

import discord
from discord.ext.commands import Context

from ...util import ChannelAndMessageId

format_tag = """
{tag_name}
{creator_snowflake_id}
{server_id}
{tag_content}
"""


def check_for_ctx(function):
    @wraps(function)
    def wrap(model, *args, **kwargs):
        if not model.ctx:
            raise NotImplementedError("context was not provided")

    return wrap


class TagsDatabase:
    __slots__ = [
        "tag_name",
        "creator_snowflake_id",
        "server_id",
        "tag_content",
        "tag_id",
        "ctx",
        "guild",
        "channel",
    ]

    def __init__(
        self,
        tag_name: Optional[str],
        creator_snowflake_id: Optional[int],
        server_id: Optional[int],
        tag_content: Optional[str],
        tag_id: Optional[int],
        ctx: Context,
    ):
        self.tag_name = tag_name
        self.creator_snowflake_id = creator_snowflake_id
        self.server_id = server_id
        self.tag_content = tag_content
        self.tag_id = tag_id
        self.ctx = ctx
        self.guild = ctx.get_guild(ChannelAndMessageId.server_id2.value)
        self.channel = discord.utils.get(self.guild.channels,
                                         id=ChannelAndMessageId.tags.value)

    async def edit(self, tag_content: str):
        msg = await self.channel.fetch_message(self.tag_id)
        message_cleanlist = msg.content.split("\n")[:3] + [tag_content]
        await msg.edit(
            suppress=True,
            content="\n".join(message_cleanlist),
            allowed_mentions=discord.AllowedMentions(everyone=False,
                                                     users=False,
                                                     roles=False,
                                                     replied_user=False),
        )

    @cache
    @lru_cache
    @check_for_ctx
    async def search(
        self,
        tag_name: Optional[str],
        creator_snowflake_id: Optional[int],
        server_id: Optional[int],
        tag_content: Optional[str],
        limit: Optional[int],
        search_all: Optional[bool] = False,
        oldest_first: Optional[bool] = False,
    ):
        tags_found = []
        if search_all:
            return await self.channel.history(
                limit=None, oldest_first=oldest_first).flatten()
        if tag_name or self.tag_name:

            def predicate(i):
                return i.content() in (tag_name, self.tag_name)

            tag_found = await self.channel.history(limit=None).get(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if creator_snowflake_id or self.creator_snowflake_id:

            def predicate(i):
                return i.content() in (creator_snowflake_id,
                                       self.creator_snowflake_id)

            tag_found = await self.channel.history(limit=None).get(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if server_id or self.server_id:

            def predicate(i):
                return i.content() in (server_id, self.server_id)

            tag_found = await self.channel.history(limit=None).get(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if tag_content or self.tag_content:

            def predicate(i):
                return i.content() in (tag_content, self.tag_content)

            tag_found = await self.channel.history(limit=None).get(predicate)
            if tag_found:
                tags_found.append(tag_found)
        return tags_found

    @classmethod
    @check_for_ctx
    async def save(self):
        local_format_tag = str(format_tag).format(
            tag_name=self.tag_name,
            creator_snowflake_id=self.creator_snowflake_id,
            server_id=self.server_id,
            tag_content=self.tag_content,
        )
        await self.channel.send(
            content=local_format_tag,
            allowed_mentions=discord.AllowedMentions(everyone=False,
                                                     users=False,
                                                     roles=False,
                                                     replied_user=False),
        )

    @classmethod
    @cache
    @check_for_ctx
    async def give_random_tag(self):
        search = await search(oldest_first=random.choice(
            [True, False], limit=random.randint(0, 500)))
        return random.choice(search)

    @staticmethod
    def create_tag_from_string(string: str):
        pass
