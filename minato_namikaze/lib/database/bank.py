from __future__ import annotations
import discord
from typing import Optional, List, Tuple, Union
from sqlalchemy import select, update, desc

from .session import session_obj
from .models_bank import BankAccount
from .config_api import Config

class InsufficientFunds(Exception):
    pass

class Bank:
    @staticmethod
    async def get_currency_name(guild: Optional[discord.Guild] = None) -> str:
        conf = Config("Economy", "bank")
        if not await Bank.is_global() and guild:
            return await conf.guild(guild).get_attr("currency_name", "credits")
        return await conf.global_().get_attr("currency_name", "credits")

    @staticmethod
    async def is_global() -> bool:
        conf = Config("Economy", "bank")
        return await conf.global_().get_attr("is_global", True)

    @staticmethod
    def _get_guild_id(user: Union[discord.Member, discord.User], is_glob: bool) -> Optional[int]:
        if is_glob:
            return None
        guild = getattr(user, "guild", None)
        return guild.id if guild else None

    @staticmethod
    async def get_balance(user: Union[discord.Member, discord.User]) -> int:
        is_glob = await Bank.is_global()
        guild_id = Bank._get_guild_id(user, is_glob)

        async with session_obj() as session:
            query = select(BankAccount.balance).where(
                BankAccount.user_id == user.id,
                BankAccount.guild_id == guild_id,
            )
            result = await session.execute(query)
            bal = result.scalar_one_or_none()
            return bal if bal is not None else 0

    @staticmethod
    async def set_balance(user: Union[discord.Member, discord.User], amount: int) -> int:
        if amount < 0:
            raise ValueError("Balance cannot be negative.")
        is_glob = await Bank.is_global()
        guild_id = Bank._get_guild_id(user, is_glob)

        async with session_obj() as session:
            query = select(BankAccount).where(
                BankAccount.user_id == user.id,
                BankAccount.guild_id == guild_id,
            )
            account = (await session.execute(query)).scalar_one_or_none()

            if not account:
                account = BankAccount(user_id=user.id, guild_id=guild_id, balance=amount)
                session.add(account)
            else:
                account.balance = amount

            await session.commit()
            return amount

    @staticmethod
    async def deposit_credits(user: Union[discord.Member, discord.User], amount: int) -> int:
        if amount < 0:
            raise ValueError("Cannot deposit negative amounts.")
        is_glob = await Bank.is_global()
        guild_id = Bank._get_guild_id(user, is_glob)

        async with session_obj() as session:
            query = select(BankAccount).where(
                BankAccount.user_id == user.id,
                BankAccount.guild_id == guild_id,
            )
            account = (await session.execute(query)).scalar_one_or_none()

            if not account:
                account = BankAccount(user_id=user.id, guild_id=guild_id, balance=amount)
                session.add(account)
            else:
                account.balance += amount

            new_bal = account.balance
            await session.commit()

        return new_bal

    @staticmethod
    async def withdraw_credits(user: Union[discord.Member, discord.User], amount: int) -> int:
        if amount < 0:
            raise ValueError("Cannot withdraw negative amounts.")
        is_glob = await Bank.is_global()
        guild_id = Bank._get_guild_id(user, is_glob)

        async with session_obj() as session:
            query = select(BankAccount).where(
                BankAccount.user_id == user.id,
                BankAccount.guild_id == guild_id,
            )
            account = (await session.execute(query)).scalar_one_or_none()

            if not account or account.balance < amount:
                raise InsufficientFunds(f"User {user.id} has insufficient funds.")

            account.balance -= amount
            new_bal = account.balance
            await session.commit()

        return new_bal

    @staticmethod
    async def transfer_credits(from_user: Union[discord.Member, discord.User], to_user: Union[discord.Member, discord.User], amount: int) -> int:
        await Bank.withdraw_credits(from_user, amount)
        await Bank.deposit_credits(to_user, amount)
        return await Bank.get_balance(from_user)

    @staticmethod
    async def get_leaderboard(guild: Optional[discord.Guild] = None, limit: int = 10) -> List[Tuple[int, int]]:
        is_glob = await Bank.is_global()
        guild_id = None if is_glob else (guild.id if guild else None)

        async with session_obj() as session:
            query = select(BankAccount.user_id, BankAccount.balance).where(
                BankAccount.guild_id == guild_id,
            ).order_by(desc(BankAccount.balance)).limit(limit)

            result = await session.execute(query)
            return [(row[0], row[1]) for row in result.all()]

bank = Bank()
