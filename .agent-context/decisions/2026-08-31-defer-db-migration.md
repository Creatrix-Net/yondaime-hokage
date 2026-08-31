# Database Reality Check: Badges and Backups

Date: 2026-08-31
Phase: 1
Status: active

## Context
During the Phase 1 database reality check, it was confirmed that `lib/database/badges.py` and `lib/database/backup.py` use Discord channels as a datastore (e.g., retrieving state by iterating channel history) rather than using the existing PostgreSQL/SQLAlchemy session. `AGENTS.md` mandates a decision on whether to migrate these to actual Postgres models in Phase 1 or defer to Phase 2.

## Options considered
- **Option A**: Migrate them to standalone SQLAlchemy 2.0 models now (Phase 1).
  - Pros: Eliminates the ugly Discord-as-a-database hack immediately.
  - Cons: Phase 2 will introduce a generalized Config abstraction. If we build bespoke tables for badges (per-user) and backups (per-guild) now, we will likely have to rewrite them in Phase 2 to use the new Config API.
- **Option B**: Defer migration to Phase 2.
  - Pros: Allows these features to directly adopt the Red-style generalized Config abstraction in Phase 2, avoiding double work.
  - Cons: The Discord datastore hack survives until Phase 2.

## Decision
**Option B**: Explicitly defer the migration of `badges.py` and `backup.py` datastores to Phase 2. 

## Reasoning
Phase 2 is specifically scoped for structural modularity and introducing a generalized Config abstraction (like Red-DiscordBot). Moving badges and backups into this new Config system is the architectural end-state. Doing a bespoke Postgres migration in Phase 1 just to satisfy the "database reality check" would be duplicate effort and counter to the goals of Phase 2. We acknowledge the technical debt and schedule its resolution for Phase 2.

## Files touched
- (None - explicitly deferred)
