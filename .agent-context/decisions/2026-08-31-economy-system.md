# Phase 3 Item 4: Economy / Currency System

Date: 2026-08-31
Phase: 3
Status: active

## Context
Phase 3 Item 4 asks for an economy/currency system. The foundation (SQLAlchemy models for BankAccount and the Bank API stub) was created during the giftdrop.py migration in Item 1. 

## Decision
- Extrapolate lib/database/bank.py to support get_balance, set_balance, withdraw_credits, 	ransfer_credits, and get_leaderboard.
- Create cogs/economy.py implementing:
  - User commands: alance, pay, daily (faucet), gamble (sink), leaderboard.
  - Admin commands: ankset global, ankset name, ankset setbal.
- Use the Config API to track timestamps for daily command cooldowns to prevent DB schema bloating.

## Files touched
- minato_namikaze/lib/database/bank.py (updated)
- minato_namikaze/cogs/economy.py (created)
