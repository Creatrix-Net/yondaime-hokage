from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from minato_namikaze.lib import Base
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy_utils import URLType

if TYPE_CHECKING:
    from minato_namikaze.lib import Context
    from .. import MinatoNamikazeBot


import logging
log = logging.getLogger(__name__)

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = {"extend_existing": True}
    guild_id = Column(BigInteger, primary_key=True)
    payment_channel = Column(BigInteger, nullable=True)
    payment_role = Column(BigInteger, nullable=True)
    payment_url = Column(URLType, nullable=True)
    


class Payments(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Handles payment related commands and features."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001F4B0")  # Money bag emoji
    
    
async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Payments(bot))
