# Legacy Migration: moderation.py collision

Date: 2026-08-31
Phase: 3
Status: active

## Context
There are two legacy moderation.py files (old_outdated/moderation.py and slash_old/moderation.py). The live bot already has a modular cogs/moderation/ package containing commands for bans, clears, roles, etc.

## Decision
- We will inspect both legacy files. Any command that already exists in cogs/moderation/ will be discarded as redundant.
- Any command not present in cogs/moderation/ will be ported using the Phase 2 Config API and permissions framework, and placed into the appropriate file in cogs/moderation/ (or a new file like cogs/moderation/misc.py).
- Once fully audited and merged, both legacy moderation.py files will be deleted.
