# Generalized Config Abstraction Architecture

Date: 2026-08-31
Phase: 2
Status: active

## Context
Phase 2 requires a "generalized Config abstraction" to replace ars.py hardcoded enums and bespoke per-cog storage, specifically referencing Red-DiscordBot's Config object. We need to design the database models that will support this in SQLAlchemy 2.0.

## Options considered
- **Option A**: A single massive EAV (Entity-Attribute-Value) table: (scope, scope_id, cog_name, key, value).
  - Pros: Only one table to manage and migrate.
  - Cons: Lack of foreign keys for strict referential integrity (if we wanted them), queries can get complicated with polymorphic scope_id.
- **Option B**: Scoped JSON tables (GlobalConfig, GuildConfig, UserConfig, ChannelConfig, RoleConfig).
  - Pros: Cleanly maps to Discord's hierarchy. Allows guild_id to be explicitly typed and indexed. Follows Red's internal PostgreSQL driver schema closely.
  - Cons: Five tables instead of one.

## Decision
**Option B**: We will implement scoped tables using SQLAlchemy 2.0 Mapped and JSON columns.
Tables:
- global_config (cog_name, key, value)
- guild_config (guild_id, cog_name, key, value)
- user_config (user_id, cog_name, key, value)
- channel_config (channel_id, cog_name, key, value)
- ole_config (role_id, cog_name, key, value)

## Reasoning
Using scoped tables provides the best indexing and conceptual map to Red's Config.guild(ctx.guild), Config.user(ctx.author), etc. Using a SQLAlchemy JSON (or JSONB) column for the alue means we don't have to enforce strict typing at the SQL level, giving cogs the flexibility to store booleans, ints, lists, or dicts without schema migrations.
