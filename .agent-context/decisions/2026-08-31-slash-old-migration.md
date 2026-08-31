# Legacy Migration: slash_old/ Directory

Date: 2026-08-31
Phase: 3
Status: active

## Context
The slash_old/ directory contains ctivities_vocaloid.py, developer.py, info.py, and moderation.py. These files implement slash commands using an ancient, pre-discord.py-2.0 syntax (discord.SlashCommand, discord.UserCommand, etc.). 

## Options considered
- **Option A**: Re-write all of them into @app_commands.command() decorators and inject them into their respective cogs.
- **Option B**: Since all the underlying logic for moderation (an, kick, warn, setup), developer tools (lacklist), and info commands already exists in the live cogs (and the newly restored old_outdated/ cogs) as prefix commands, these slash command wrappers are redundant. Discord.py 2.0 supports @commands.hybrid_command() which trivially exposes prefix commands as slash commands. The actual app-command coverage should be applied directly to the main cogs via hybrid_command instead of maintaining separate, duplicate "slash" cogs.

## Decision
**Option B**: The contents of slash_old/ are structurally obsolete and duplicate the underlying logic of the main cogs. Rather than porting redundant command wrappers, we will document them as completely superseded by the primary cogs in cogs/ (which can be hybridized later if slash commands are desired). The files in slash_old/ will be deleted as they have been confirmed redundant.

## Files touched
- minato_namikaze/slash_old/activities_vocaloid.py (deleted)
- minato_namikaze/slash_old/developer.py (deleted)
- minato_namikaze/slash_old/info.py (deleted)
- minato_namikaze/slash_old/moderation.py (deleted)
