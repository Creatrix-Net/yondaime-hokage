import logging

from discord.ext.commands import Context

from ..util import ChannelAndMessageId

log = logging.getLogger(__name__)


class Badges:
    """A database handler for the Badges class"""

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.channel = ctx.get_config_channel_by_name_or_id(
            ChannelAndMessageId.badges_channel.value
        )

    async def get_all_badges(self) -> list:
        """|coro|
        Returns all the badges

        :return: List of all badges data
        :rtype: list
        """
        # async for i in self.channel.history(limit=None):
        #     set_dict.add({'filename': ''})
        return [
            dict(
                badge_name=i.content,
                code=self.get_badge_code(i.content),
                file_name=i.attachments[0],
                is_inverted=False,
            )
            async for i in self.channel.history(limit=None)
        ]

    @staticmethod
    def get_badge_code(badge_name: str) -> str:
        """Returns the badge code from its name

        :param badge_name: The name of the badge image
        :type badge_name: str
        :return: Badge Code
        :rtype: str
        """
        return "".join(list(i[0].upper() for i in badge_name.split(" ")))
