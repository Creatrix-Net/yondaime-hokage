# Discord.py Currency Pass - Avatars and Embed.Empty

Date: 2026-08-31
Phase: 1
Status: active

## Context
During the Phase 1 currency audit, several discord.py v1.x and early v2.0 paradigms were found:
1. `user.avatar.url` accesses crash when a user has a default avatar (because `avatar` is `None` in discord.py v2.0+). The correct property is `.display_avatar.url` which returns the default avatar seamlessly.
2. `discord.Embed.Empty` is deprecated in discord.py v2.0+ in favor of just using `None`.

## Options considered
- Fix manually when reported by users vs. systemic sweep.

## Decision
Systemically replaced all instances of `.avatar.url` and `.avatar_url` with `.display_avatar.url`. Replaced all instances of `discord.Embed.Empty` with `None`.

## Reasoning
This prevents unconditional exceptions for users with default avatars, which is a common source of instability. It aligns with modern discord.py guidelines (v2.0+).

## Files touched
- `minato_namikaze/discordbot.py`
- `minato_namikaze/cogs/anime_and_vocaloids/anime_and_waifu.py`
- `minato_namikaze/cogs/dev/developer.py`
- `minato_namikaze/cogs/events/cmd_error.py`
- `minato_namikaze/cogs/fun/random_fun_games.py`
- `minato_namikaze/cogs/info/mysupport.py`
- `minato_namikaze/cogs/info/serverinfo.py`
- `minato_namikaze/cogs/info/snipe.py`
- `minato_namikaze/lib/functions/moderation.py`
- `minato_namikaze/lib/util/paginator.py`
