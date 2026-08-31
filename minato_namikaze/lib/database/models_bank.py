from __future__ import annotations
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from .config import Base

class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=True, index=True) # None for global
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
