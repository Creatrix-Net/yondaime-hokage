# Legacy Migration: dminvites.py Collision

Date: 2026-08-31
Phase: 3
Status: active

## Context
While migrating old_outdated/dminvites.py, it was discovered that its core logic (responding to Discord invites sent to the bot in DMs) has already been rebuilt into cogs/dev/developer.py (lines 466-476). developer.py hardcodes the response message, whereas dminvites.py originally provided commands ([p]dminvite settings, [p]dminvite message) to configure this globally.

## Options considered
- **Option A**: Port dminvites.py as a standalone cog (cogs/dminvites.py) and remove the duplicate on_message logic from developer.py.
  - Pros: Keeps the bot owner's DM invite configuration isolated.
  - Cons: Splitting DM event handlers across multiple cogs unnecessarily.
- **Option B**: Merge the configuration commands (dminvite group) directly into developer.py (where the event listener already lives) and use the Phase 2 Config API to store the custom message. Delete dminvites.py as it's fully absorbed.
  - Pros: Keeps all bot-developer configuration together. Removes duplicate event listener logic.

## Decision
**Option B**: We will merge the dminvite configuration commands into cogs/dev/developer.py, update the existing on_message listener in developer.py to use the Config API, and then delete old_outdated/dminvites.py.

## Files touched
- minato_namikaze/cogs/dev/developer.py (modified)
- minato_namikaze/old_outdated/dminvites.py (deleted/absorbed)
