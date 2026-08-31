from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from .config import GlobalConfig, GuildConfig, UserConfig, ChannelConfig, RoleConfig
from .session import session_obj

log = logging.getLogger(__name__)


class Group:
    def __init__(self, table, entity_id: int | None, cog_name: str):
        self.table = table
        self.entity_id = entity_id
        self.cog_name = cog_name

    async def get_attr(self, key: str, default: Any = None) -> Any:
        async with session_obj() as session:
            stmt = select(self.table.value).where(
                self.table.cog_name == self.cog_name,
                self.table.key == key,
            )
            if self.entity_id is not None:
                id_col = list(self.table.primary_key.columns)[0]
                stmt = stmt.where(id_col == self.entity_id)

            result = await session.execute(stmt)
            val = result.scalar_one_or_none()
            if val is None:
                return default
            return val

    async def set_attr(self, key: str, value: Any) -> None:
        async with session_obj() as session:
            id_col_name = list(self.table.primary_key.columns)[0].name

            values = {
                "cog_name": self.cog_name,
                "key": key,
                "value": value,
            }
            if self.entity_id is not None:
                values[id_col_name] = self.entity_id

            stmt = (
                insert(self.table)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=[col.name for col in self.table.primary_key.columns],
                    set_={"value": value},
                )
            )
            await session.execute(stmt)
            await session.commit()


class Config:
    @classmethod
    def get_conf(cls, cog_instance: Any, identifier: str) -> Config:
        cog_name = getattr(
            cog_instance, "qualified_name", cog_instance.__class__.__name__
        )
        return cls(cog_name, identifier)

    def __init__(self, cog_name: str, identifier: str):
        self.cog_name = cog_name
        self.identifier = identifier

    def global_(self):
        return Group(GlobalConfig, None, self.cog_name)

    def guild(self, guild):
        return Group(GuildConfig, guild.id, self.cog_name)

    def user(self, user):
        return Group(UserConfig, user.id, self.cog_name)

    def channel(self, channel):
        return Group(ChannelConfig, channel.id, self.cog_name)

    def role(self, role):
        return Group(RoleConfig, role.id, self.cog_name)
