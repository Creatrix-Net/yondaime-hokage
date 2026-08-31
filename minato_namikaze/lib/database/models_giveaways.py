from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .config import Base


class Giveaway(Base):
    __tablename__ = "giveaways"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    host_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    prize: Mapped[str] = mapped_column(String(500), nullable=False)
    winners_count: Mapped[int] = mapped_column(Integer, default=1)

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    ended: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Requirements & Weights config
    # Example: {"role_id": 12345} -> must have role
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    # Example: {"role_id": 3} -> if user has role, they get 3 entries
    weights: Mapped[dict] = mapped_column(JSON, default=dict)


class GiveawayEntry(Base):
    __tablename__ = "giveaway_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    giveaway_message_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("giveaways.message_id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    entries: Mapped[int] = mapped_column(Integer, default=1)
