import discord
from typing import Optional
from sqlalchemy import select

from .session import session_obj
from .models_bank import BankAccount
from .config_api import Config

class Bank:
    @staticmethod
    async def get_currency_name(guild: Optional[discord.Guild] = None) -> str:
        conf = Config("Economy", "bank")
        if guild:
            return await conf.guild(guild).get_attr("currency_name", "credits")
        return await conf.global_().get_attr("currency_name", "credits")
        
    @staticmethod
    async def is_global() -> bool:
        conf = Config("Economy", "bank")
        return await conf.global_().get_attr("is_global", True)

    @staticmethod
    async def deposit_credits(user: discord.Member, amount: int) -> int:
        is_glob = await Bank.is_global()
        guild_id = None if is_glob else user.guild.id
        
        async with session_obj() as session:
            query = select(BankAccount).where(
                BankAccount.user_id == user.id,
                BankAccount.guild_id == guild_id
            )
            result = await session.execute(query)
            account = result.scalar_one_or_none()
            
            if not account:
                account = BankAccount(user_id=user.id, guild_id=guild_id, balance=amount)
                session.add(account)
            else:
                account.balance += amount
                
            new_bal = account.balance
            await session.commit()
            
        return new_bal

bank = Bank()
