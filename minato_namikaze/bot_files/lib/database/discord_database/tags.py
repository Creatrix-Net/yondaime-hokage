import random
from datetime import datetime
from orjson import dumps
import json
import io
from functools import cache, cached_property, lru_cache, wraps
from typing import Optional, Union, Literal
from ...util.vars import ChannelAndMessageId

import discord
from discord.ext.commands import Context

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
        return (
            "The tag with that name does not exists!"
        )

class TagsDatabase:
    def __init__(self, ctx: Optional[Context] = None, name: Optional[str] = None, content: Optional[str]= None, owner_id: Optional[int]= None, server_id: Optional[int]= None, created_at: Optional[datetime] = None, aliases: Optional[Union[list]] = []):
        self.name=name
        self.content=content
        self.owner_id=owner_id
        self.server_id=server_id
        self.created_at=created_at
        self.aliases = aliases
        self.ctx: Context = ctx
        if ctx is not None:
            self.tags_channel = ctx.get_config_channel_by_name_or_id(ChannelAndMessageId.tags.value)
            self.tags_aliases_channel = ctx.get_config_channel_by_name_or_id(ChannelAndMessageId.tags_aliases.value)
    
    @check_for_ctx
    def channel(self):
        return self.ctx.get_config_channel_by_name_or_id(ChannelAndMessageId.tags.value)
    
    
    async def add_aliases(self, name:str, server_id: Optional[int]):
        #raise uniqueviolationerror
        pass

    async def edit(self, tag_content: str):
        msg = await self.channel.fetch_message(self.tag_id)
        message_cleanlist = msg.content.split("\n")[:3] + [tag_content]
        await msg.edit(
            suppress=True,
            content="\n".join(message_cleanlist),
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=False, roles=False, replied_user=False
            ),
        )

    @cache
    @lru_cache
    @check_for_ctx
    async def search(
        self,
        name: Optional[str],
        owner_id: Optional[int],
        server_id: Optional[int],
        limit: Optional[int],
        get_only_name: Optional[Union[bool, Literal[False]]],
        search_all: Optional[Union[bool, Literal[False]]],
        oldest_first: Optional[Union[bool, Literal[False]]],
        exact: bool = False
    ):
        tags_found = []
        if search_all:
            return await self.channel.history(
                limit=None, oldest_first=oldest_first
            ).flatten()
        
        #Name    
        if name or self.name:
            async def predicate(i):
                data = json.load(await i.attachments[0].read())
                return data['name'].lower() in (name.lower(), self.name.lower()) if not exact else data['name'].lower() == name or data['name'].lower() == self.name.lower()
            tag_found = await self.channel.history(limit=None).find(await predicate)
            if tag_found:
                tags_found.append(tag_found)
        
        #Owner ID        
        if owner_id or self.owner_id:
            async def predicate(i):
                data = json.load(await i.attachments[0].read())
                return data['owner_id'].lower() in (owner_id.lower(), self.owner_id.lower())  if not exact else data['owner_id'] == owner_id or data['owner_id'] == self.owner_id
            tag_found = await self.channel.history(limit=None).find(await predicate)
            if tag_found:
                tags_found.append(tag_found)
        
        #Guild ID        
        if server_id or self.server_id:
            async def predicate(i):
                data = json.load(await i.attachments[0].read())
                return data['server_id'] in (server_id, self.server_id) if not exact else data['server_id'] == server_id or data['server_id'] == self.server_id
            tag_found = await self.channel.history(limit=None).find(predicate)
            if tag_found:
                tags_found.append(tag_found)
         
        #remove duplicates        
        if tags_found and get_only_name:
            tags_found = map(lambda a: a.get('name'),tags_found)
            
        return list(set(tags_found)) if tags_found else None
    
    def get_object_in_dict(self, include_ctx: Optional[Union[bool, Literal[False]]] = False):
        data = dict(
            name=self.name,
            content=self.content,
            owner_id=self.owner_id,
            server_id=self.server_id,
            created_at=self.created_at,
            aliases=self.aliases
        )
        if include_ctx:
            data.update({'ctx': self.ctx})
        return data

    @check_for_ctx
    async def save(self):
        data = self.get_object_in_dict()
        if self.search(exact=True, name=data['name']) is not None:
            raise UniqueViolationError('The tag already exists')
        json_bytes = dumps(data)
        await self.tags_channel.send(
            content=data['name'],
            file=discord.File(io.BytesIO(json_bytes), filename=f"{data['name']}.json"),
        )

    @cache
    @check_for_ctx
    async def give_random_tag(self, guild: Optional[int]):
        search = await self.search(oldest_first=random.choice([True, False], limit=random.randint(0, 500)), server_id=guild)
        return random.choice(search)