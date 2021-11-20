from typing import Optional, Union

import discord
from discord.ext.commands import Context

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

    async def edit(self, tag_content: str):
        msg = await self.ctx.fetch_message(self.tag_id)
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

    def save(self):
        global format_tag
        pass
