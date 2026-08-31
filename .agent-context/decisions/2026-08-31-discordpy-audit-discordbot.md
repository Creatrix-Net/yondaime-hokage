# discord.py currency audit — discordbot.py

Date: 2026-08-31
Phase: 1
Status: active

## Context
Phase 1 requires a discord.py currency audit: diffing current code against
the latest stable discord.py and fixing deprecated API usage. This decision
covers the specific issues found in `discordbot.py` and the chosen fixes.

## Options considered

### Intents strategy
- Option A: Keep `.all()` but document why — Pros: no risk of missing an
  intent some cog needs. Cons: over-broad, security/verification problem,
  masks the deprecated alias names (`bans`, `emojis`).
- **Option B (chosen)**: Replace with explicit intents listing only what's
  needed — Pros: transparent, follows AGENTS.md guidance, uses modern
  aliases. Cons: if a cog needs an intent we miss, it will silently fail.
  Mitigation: audit cog event handlers before committing.

### Duplicate `get_random_image_from_tag`
- Option A: Keep both, rename sync version — Pros: preserves sync API.
  Cons: sync version makes blocking calls in async context (performance
  hazard), and nothing in the codebase calls the sync version (it's shadowed
  by the async def with the same name).
- **Option B (chosen)**: Delete the sync version — the async version is the
  only one that's actually callable due to Python's name-shadowing semantics.

### Discriminator logic in `query_member_named`
- Option A: Keep as-is — Pros: zero risk. Cons: dead code, misleading.
- **Option B (chosen)**: Remove the discriminator branch — Discord removed
  discriminators in June 2023. The branch is unreachable in practice. If any
  edge case exists, `query_members` will still find the user by username.

### `process_commands` unconditional message deletion
- Option A: Remove the `finally` delete — Pros: stops surprising behavior.
  Cons: this may be intentional (the bot deletes command messages to keep
  channels clean). Without the owner confirming, removing it would be a
  behavior change.
- **Option B (chosen)**: Add a documenting comment explaining the behavior,
  flag it as a candidate for per-guild configurability in Phase 2.

## Decision
Fix all 5 issues in separate commits as described in the implementation plan.
The intents fix requires an audit of cog event handlers to ensure no needed
intent is dropped.

## Reasoning
All changes align with Phase 1's goal of running on current, secure,
non-deprecated foundations without changing user-facing behavior. The only
borderline case is the discriminator removal, which removes dead code but
could theoretically affect a user with a legacy discriminator — the risk is
negligible since Discord completed the migration in 2023.

## Files touched
- `minato_namikaze/discordbot.py` — all changes in this decision
