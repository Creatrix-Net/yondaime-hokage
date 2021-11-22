from typing import Optional, Union

import discord
from discord.ext.commands import Context

from ..util import ChannelAndMessageId

format_tag = """
{tag_name}
{creator_snowflake_id}
{server_id}
{tag_content}
"""


class Tags:
    __slots__ = [
        "tag_name",
        "creator_snowflake_id",
        "server_id",
        "tag_content",
        "tag_id",
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
        self.guild = ctx.bot.get_guild(ChannelAndMessageId.server_id2.value)
        self.channel = discord.utils.get(guild.channels,
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

    def search_tag(
        self,
        tag_name: Optional[str],
        creator_snowflake_id: Optional[int],
        server_id: Optional[int],
        tag_content: Optional[str],
    ):
        pass

    async def save(self):
        global format_tag
        local_format_tag = str(format_tag).format(
            tag_name=self.tag_name,
            creator_snowflake_id=self.creator_snowflake_id,
            server_id=self.server_id,
            tag_content=self.tag_content,
        )
        await self.channel.send(content=local_format_tag)
