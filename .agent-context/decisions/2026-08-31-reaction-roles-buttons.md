# Legacy Migration: Reaction Roles (Item 2)

Date: 2026-08-31
Phase: 3
Status: active

## Context
Phase 3 Item 2 requires replacing the old emoji-reaction interaction for Reaction Roles with a persistent discord.ui.View/Button-based UI.

## Decision
- Rewrite cogs/reaction_roles.py to use Config API instead of SQLAlchemy.
- Create a RoleButton(discord.ui.Button) and a PersistentRoleView(discord.ui.View).
- Register all persistent views in the cog to ensure they survive bot restarts.

## Files touched
- minato_namikaze/cogs/reaction_roles.py
