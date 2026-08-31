# Config-Driven Permissions Framework Architecture

Date: 2026-08-31
Phase: 2
Status: active

## Context
Phase 2 requires a config-driven permissions framework to allow per-guild command overrides. We need a way to override default Discord permissions and say "Command X can only be used by Role Y or in Channel Z".

## Options considered
- **Option A**: Build a bespoke permissions table in SQLAlchemy.
  - Pros: Highly relational, can use SQL joins to resolve permissions fast.
  - Cons: Re-invents the wheel. We just built a generalized Config abstraction designed exactly for this kind of dynamic JSON-based configuration.
- **Option B**: Store permission overrides using the new Config abstraction.
  - Pros: Utilizes the GuildConfig table we just created. Extremely flexible. Maps nicely to Red-DiscordBot's model.
  - Cons: Requires pulling JSON blobs during command invocation (though SQLAlchemy caches/async execution makes this fast enough for our scale).

## Decision
**Option B**: We will use the new Config API to store permission overrides under the Core cog config: Config("Core", "permissions").guild(ctx.guild).get_attr("overrides").
We will add a global @bot.check that intercepts commands, looks up their qualified name in the overrides dictionary, and validates if the user meets the configured Role, User, or Channel overrides.

## Reasoning
The core goal of Phase 2 is to leverage the generalized Config abstraction. Building permissions on top of it proves the abstraction's viability and keeps the schema simple.
