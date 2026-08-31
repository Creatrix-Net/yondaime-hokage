# Cog Boundary Cleanup Decision

Date: 2026-08-31
Phase: 2
Status: active

## Context
Phase 2 mandates "Cog boundary cleanup" to move single-cog-specific logic out of lib/ and into the cogs themselves. lib/ should only contain cross-cutting logic.

## Decision
We will move the following single-use classes and functions into their respective cogs:
1. lib/functions/meek_moe.py -> moved directly into cogs/anime_and_vocaloids/vocaloid.py.
2. lib/classes/badge_entry.py -> moved directly into cogs/badges.py.
3. lib/classes/music.py -> moved directly into cogs/music.py.
4. lib/classes/reaction_roles.py -> moved directly into cogs/reaction_roles.py.

## Reasoning
These files are only used by a single cog. Keeping them in lib/ violates the modular boundary of the cog (if you delete the cog, the logic should go with it). We will inline them directly into the target .py files because they are small enough, or keep them adjacent, but moving them inside the cog file is cleaner for a single-file cog architecture.
