# Remove User Discriminator Logic

Date: 2026-08-31
Phase: 1
Status: active

## Context
Discord removed the `#0000` discriminator system in favor of unique usernames in 2023. The `yondaime-hokage` codebase, particularly in `cogs/moderation/backup.py` and `cogs/badges.py`, still contains hardcoded string splitting (e.g. `split("#")`) and `.discriminator` accesses. This breaks functionality for all users on the new username system.

## Options considered
- **Option A**: Fallback to checking `.discriminator == '0'` as a proxy for new usernames.
  - Pros: Minimal logic change.
  - Cons: Fundamentally broken string manipulations will still occur; doesn't fix `split("#")` crashes if no `#` exists in older stored strings.
- **Option B**: Completely remove `.discriminator` references and update formatting strings to only use `.name` or `.display_name`. Handle legacy `#` in stored strings gracefully.
  - Pros: Correct long-term fix aligned with discord.py v2.0+ and modern Discord.
  - Cons: Might change some minor logging formats.

## Decision
**Option B**: Completely remove all references to `.discriminator` and `split("#")` on user objects. Replace formatted representations of users with just their `.name` (or `.global_name`/`.display_name` where appropriate). For parsing existing records, tolerate the absence of `#`.

## Reasoning
This is required for basic functionality on modern Discord. Without this, `badges.py` profile commands crash unconditionally for new users, and `backup.py` backups fail to serialize/deserialize correctly.

## Files touched
- `minato_namikaze/cogs/moderation/backup.py`
- `minato_namikaze/cogs/badges.py`
