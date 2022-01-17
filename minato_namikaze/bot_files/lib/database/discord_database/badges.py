from typing import AsyncIterator

from discord.ext.commands import Context

from ...util import ChannelAndMessageId


class Badges:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.channel = ctx.get_config_channel_by_name_or_id(
            ChannelAndMessageId.badges_channel.value)

    async def get_all_badges(self) -> list:
        return [
            dict(
                badge_name=i.content,
                code=self.get_badge_code(i.content),
                file_name=i.attachments[0],
                is_inverted=False,
            ) async for i in self.channel.history(limit=None)
        ]

    @staticmethod
    def get_badge_code(badge_name: str) -> str:
        return "".join([i[0] for i in badge_name.split(" ")])
