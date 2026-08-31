# Legacy Migration: giveaway.py

Date: 2026-08-31
Phase: 3
Status: active

## Context
old_outdated/giveaway.py contains the old giveaway cog. Phase 3 Item 3 requires a database-backed, Red-style giveaway system, but Item 1 requires moving the legacy files back first. To satisfy Item 1, we will port this file "as-is" to cogs/giveaway.py but rewrite its basic data access to use the Phase 2 Config API and fix any async blocking/deprecation issues. We'll leave the advanced Red-style features (persistent entries, multi-winner reroll, requirements) for the dedicated Item 3 pass.

## Decision
- Move old_outdated/giveaway.py to cogs/giveaway.py.
- Rewrite ad-hoc ot.giveaway state or file-based JSON to use the new Config("Giveaway", "data") API.
- Keep the cog functional so it runs on Phase 2 architecture.

## Files touched
- minato_namikaze/cogs/giveaway.py
- minato_namikaze/old_outdated/giveaway.py (deleted)
