from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..util import envConfig

log = logging.getLogger(__name__)


class Session:
    """
    This class is used to create a session with the database.
    """

    @staticmethod
    def get_engine() -> AsyncEngine:
        """
        This function is used to get the engine for the database.
        """
        return create_async_engine(envConfig.DATABASE_URL, echo=False)

    @staticmethod
    def get_session() -> async_sessionmaker[AsyncSession]:
        """Return the database session connection."""
        db_session = async_sessionmaker(
            bind=Session.get_engine(),
            autoflush=True,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        return db_session


session_obj: async_sessionmaker[AsyncSession] = Session.get_session()
