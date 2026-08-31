# Phase 3 Item 3: Giveaways Rebuild

Date: 2026-08-31
Phase: 3
Status: active

## Context
Giveaways (migrated to cogs/giveaway.py in Item 1) currently rely on a basic Config-based active list and text commands. Item 3 requires a full database-backed rewrite mimicking Red-DiscordBot's advanced features, including entry requirements, role weights, and button-based interactions (leveraging the patterns established in Item 2).

## Decision
- Create explicit SQLAlchemy models in lib/database/models_giveaways.py (Giveaway, GiveawayEntry) to handle large participant counts natively instead of bloating the Config API JSON storage.
- Implement a GiveawayView(discord.ui.View) with a persistent "🎉 Join" button.
- Advanced features:
  - **Requirements**: Store required roles as JSON in the Giveaway model. The button callback evaluates this before granting entry.
  - **Weights**: Store role multipliers as JSON in the Giveaway model. The button callback calculates the user's highest applicable multiplier and stores it as their entry weight in GiveawayEntry.
- Background task polls for expired giveaways and resolves winners, expanding the participant pool by entry weights to ensure fairness.

## Files touched
- minato_namikaze/lib/database/models_giveaways.py (created)
- minato_namikaze/lib/database/alembic/env.py (modified)
- minato_namikaze/cogs/giveaway.py (rewritten)
