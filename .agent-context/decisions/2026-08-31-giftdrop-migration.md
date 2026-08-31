# Legacy Migration: giftdrop.py

Date: 2026-08-31
Phase: 3
Status: active

## Context
old_outdated/giftdrop.py is a cashdrop cog (borrowed from Red-DiscordBot) that relies on edbot.core.bank and edbot.core.Config.

## Decision
- We will rewrite it to use minato_namikaze.lib.database.config_api.Config.
- We will create a stub for minato_namikaze.lib.database.bank with SQLAlchemy models (BankAccount) and deposit_credits() so that giftdrop.py works seamlessly. This also lays the groundwork for the Economy system (Phase 3 Item 4).
- The MessagePredicate from Red will be replaced with a standard discord.ext.commands check function.
- It will be moved to minato_namikaze/cogs/fun/giftdrop.py.

## Files touched
- minato_namikaze/lib/database/models_bank.py (created)
- minato_namikaze/lib/database/bank.py (created)
- minato_namikaze/cogs/fun/giftdrop.py (migrated)
- minato_namikaze/old_outdated/giftdrop.py (deleted)
