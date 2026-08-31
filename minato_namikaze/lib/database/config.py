from __future__ import annotations

from sqlalchemy import BigInteger, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..util.vars import Base

class GlobalConfig(Base):
    __tablename__ = "global_config"

    cog_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

class GuildConfig(Base):
    __tablename__ = "guild_config"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cog_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

class UserConfig(Base):
    __tablename__ = "user_config"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cog_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

class ChannelConfig(Base):
    __tablename__ = "channel_config"

    channel_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cog_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

class RoleConfig(Base):
    __tablename__ = "role_config"

    role_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cog_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
