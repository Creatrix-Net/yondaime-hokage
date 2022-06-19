import logging

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.orm import relationship

from ..util import Base

log = logging.getLogger(__name__)


class Premium(Base):
    __tablename__ = "premium"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)
    reaction_roles_amount = Column(SmallInteger, nullable=False)
    reminders_amount = Column(SmallInteger, nullable=False)
    reminder_amount_per_user = Column(SmallInteger, nullable=False)
    no_vote_locked = Column(Boolean, default=False, nullable=False)
    no_of_servers_applicable = Column(SmallInteger, nullable=False)
    users = relationship("User", backref="premium")

    def __repr__(self) -> str:
        return f"<Premium(id={self.id!r}, name={self.name!r})>"

    def __str__(self) -> str:
        return self.__repr__()


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    premium_id = Column(Integer, ForeignKey("premium.id"), nullable=True)
    premium_expiry = Column(DateTime, nullable=True)
    applicable_servers_for_premium = relationship(
        "Server", backref="premium_given_by_user"
    )
    blacklisted = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, premium_id={self.premium_id!r}, premium_expiry={self.premium_expiry!r})>"

    def __str__(self) -> str:
        return self.__repr__()


class Server(Base):
    __tablename__ = "server"
    id = Column(BigInteger, primary_key=True)
    premium_applier_user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    blacklisted = Column(Boolean, default=False, nullable=False)
    show_404_commands_error = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Server(id={self.id!r}, premium_applier_user_id={self.premium_applier_user_id!r})>"

    def __str__(self) -> str:
        return self.__repr__()
