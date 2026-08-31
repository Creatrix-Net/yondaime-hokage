# Phase 3 Item 5: Games and UX enhancements

Date: 2026-08-31
Phase: 3
Status: active

## Context
Phase 3 Item 5 requested the addition of 3 game cogs (counting, higher-or-lower, trivia) and a "did-you-mean" fallback for mis-typed commands.

## Decision
- Developed cogs/fun/counting.py relying on Config API for per-channel counting progress and user locks.
- Developed cogs/fun/higher_or_lower.py and cogs/fun/trivia.py employing discord.ui.View patterns rather than message listeners to ensure cleaner user interaction. Trivia pulls from the OpenTDB API directly.
- Spliced difflib.get_close_matches into the CommandNotFound block inside cogs/events/cmd_error.py to auto-suggest valid bot commands dynamically.

## Files touched
- minato_namikaze/cogs/events/cmd_error.py
- minato_namikaze/cogs/fun/counting.py (created)
- minato_namikaze/cogs/fun/higher_or_lower.py (created)
- minato_namikaze/cogs/fun/trivia.py (created)
