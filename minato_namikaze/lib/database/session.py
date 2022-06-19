import logging
from contextlib import contextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker

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
        return create_async_engine(envConfig.DATABASE_URL, echo=True)

    @staticmethod
    def get_session() -> sessionmaker:
        """Return the database session connection."""
        db_session = sessionmaker(
            bind=Session.get_engine(),
            autoflush=True,
            autocommit=True,
            class_=AsyncSession,
            max_size=20,
            min_size=20,
        )
        return db_session()

    @contextmanager
    def session_manager() -> sessionmaker:
        """Provides a transactional scope around a series of operations."""
        session = Session.get_session()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def execute(model_query: Any) -> None:
        """Execute the database session."""
        with Session.session_manager() as session:
            session.add(model_query)
            session.commit()
