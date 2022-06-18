import logging

from sqlalchemy import BigInteger, Boolean, Column, String, SmallInteger, DateTime
from sqlalchemy.orm import declarative_base, relationship

log = logging.getLogger(__name__)

Base = declarative_base()


class Premium(Base):
    __tablename__ = "premium"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    reaction_roles_amount = Column(SmallInteger, nullable=False)
    reminders_amount = Column(SmallInteger, nullable=False)
    reminder_amount_per_user = Column(SmallInteger, nullable=False)
    no_vote_locked = Column(Boolean, default=False, nullable=False)
    no_of_servers_applicable = Column(SmallInteger, nullable=False)


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    premium = relationship("Premium")
    premium_expiry = Column(DateTime, nullable=False)
    applicable_servers = Column(SmallInteger, nullable=False)


class Server(Base):
    __tablename__ = "server"
    id = Column(BigInteger, primary_key=True)
    premium_given_by = relationship("User")
