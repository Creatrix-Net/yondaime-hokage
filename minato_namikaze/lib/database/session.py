from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..util import envConfig


def get_session() -> sessionmaker:
    """Return the database session connection."""
    engine =  create_async_engine(envConfig.DATABASE_URL, echo=True)
    db_session = sessionmaker(bind=engine, autoflush=True, autocommit=True, class_=AsyncSession, pool_recycle=3600)
    return db_session()
