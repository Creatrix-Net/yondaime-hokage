import random
from datetime import datetime
from functools import cache, cached_property, lru_cache, wraps
from typing import Literal, NamedTuple, Optional, Union

import discord
import orjson
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
            raise RuntimeError("context was not provided")

    return wrap


class UniqueViolationError(ValueError):
    pass


class TagsDoesNotExistsError(Exception):
    def __str__(self):
        return "The tag with that name does not exists!"


class TagsDatabase(NamedTuple):
    ctx: Context

    @property
    def channel(
        self,
        name: Optional[str],
        content: Optional[str],
        owner_id: Optional[int],
        server_id: Optional[int],
        created_at: Optional[datetime],
        uses: Optional[int],
    ):
        self.name = name
        self.content = content
        self.owner_id = owner_id
        self.server_id = server_id
        self.created_at = created_at
        self.uses = uses
        self.aliases = Optional[Union[list, Literal[[]]]]
        return self.ctx.get_config_channel_by_name_or_id(
            ChannelAndMessageId.tags.value)

    async def add_aliases(self, tag_name: str, server_id: Optional[int]):
        # raise uniqueviolationerror
        pass

    async def increase_usage(
        self,
        tag_name: str,
        server_id: Optional[int],
        amount: Optional[Union[int, Literal[1]]],
    ):
        pass

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
        get_only_name: Optional[Union[bool, Literal[False]]],
        search_all: Optional[Union[bool, Literal[False]]],
        oldest_first: Optional[Union[bool, Literal[False]]],
    ):
        tags_found = []
        if search_all:
            return await self.channel.history(
                limit=None, oldest_first=oldest_first).flatten()
        if tag_name or self.tag_name:

            def predicate(i):

                return i.content() in (tag_name, self.tag_name)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if creator_snowflake_id or self.creator_snowflake_id:

            def predicate(i):
                return i.content() in (creator_snowflake_id,
                                       self.creator_snowflake_id)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if server_id or self.server_id:

            def predicate(i):
                return i.content() in (server_id, self.server_id)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if tag_content or self.tag_content:

            def predicate(i):
                return i.content() in (tag_content, self.tag_content)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if tags_found and get_only_name:
            tags_found = map(lambda a: a.get("name"), tags_found)
        return list(set(tags_found)) if tags_found else None

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
    @check_for_ctx
    async def do_exact_search(
        self,
        tag_name: Optional[str],
        creator_snowflake_id: Optional[int],
        server_id: Optional[int],
        tag_content: Optional[str],
        limit: Optional[int],
        get_only_name: Optional[Union[bool, Literal[False]]],
    ):
        tags_found = []
        if tag_name or self.tag_name:

            def predicate(i):
                return (i.content().lower() == tag_name
                        or i.content().lower() == self.tag_name)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if creator_snowflake_id or self.creator_snowflake_id:

            def predicate(i):
                return (i.content().lower() == creator_snowflake_id
                        or i.content().lower() == self.creator_snowflake_id)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if server_id or self.server_id:

            def predicate(i):
                return (i.content().lower() == server_id
                        or i.content().lower() == self.server_id)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if tag_content or self.tag_content:

            def predicate(i):
                return (i.content().lower() == tag_content
                        or i.content().lower() == self.tag_content)

            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
        if tags_found and get_only_name:
            tags_found = map(lambda a: a.get("name"), tags_found)
        return list(set(tags_found)) if tags_found else None

    @classmethod
    @cache
    @check_for_ctx
    async def give_random_tag(self, guild: Optional[int]):
        search = await self.search(
            oldest_first=random.choice([True, False],
                                       limit=random.randint(0, 500)),
            server_id=guild,
        )
        return random.choice(search)

    @staticmethod
    def create_tag_from_string(string: str):
        pass
