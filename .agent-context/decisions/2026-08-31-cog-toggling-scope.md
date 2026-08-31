# Per-Guild Feature Toggling Scope

Date: 2026-08-31
Phase: 2
Status: active

## Context
Phase 2 calls for "Per-guild cog/feature toggling" inspired by Red-DiscordBot. Red's ecosystem includes a Downloader cog that allows installing, updating, and removing cogs from third-party repositories dynamically. We need to decide if that level of dynamic installation is in scope, or if we just want a way to enable/disable built-in feature categories per guild.

## Options considered
- **Option A**: Full Red-style Downloader.
  - Pros: 1:1 parity with Red's expansiveness.
  - Cons: Extremely high surface area for bugs, security risks (arbitrary code execution), and dependency management nightmares. Requires architectural changes to the bot's loading sequence.
- **Option B**: Built-in Category Enable/Disable only.
  - Pros: Keeps the monolithic repo structure intact while fulfilling the core requirement: giving server admins control over what features run in their guild. Highly secure and deterministic.
  - Cons: Less extensible for third parties (must PR to the main repo).

## Decision
**Option B**: We will build a per-guild enable/disable system for built-in cogs, backed by the new Config abstraction. We will not build a dynamic third-party cog downloader.

## Reasoning
The primary benefit of Red's toggling for a centralized bot like this is reducing admin friction (e.g., turning off leveling or music in a specific server), not enabling arbitrary 3rd party plugins. A simple config-driven allow/deny list per guild is sufficient, secure, and fits Phase 2's timeframe.
