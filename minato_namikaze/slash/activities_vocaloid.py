import typing
import discord

from discord.abc import GuildChannel
from discord import application_command_option, VoiceChannel

activities = [
    "youtube",
    "poker",
    "chess",
    "betrayal",
    "fishing",
    "letter-league",
    "word-snack",
    "sketch-heads",
    "spellcast",
    "awkword",
    "checkers",
]


activities = [
    "youtube",
    "poker",
    "chess",
    "betrayal",
    "fishing",
    "letter-league",
    "word-snack",
    "sketch-heads",
    "spellcast",
    "awkword",
    "checkers",
]


class Activities(discord.SlashCommand):
    """Get access to discord beta activities feature"""

    activities: typing.Literal["youtube", "poker", "chess", "betrayal", "fishing", "letter-league","word-snack", "sketch-heads", "spellcast", "awkword","checkers", ] = discord.application_command_option(
            description="The type of activity",
            default="youtube",
    )

    voice_channel: GuildChannel = application_command_option(channel_types=[VoiceChannel],description="A voice channel in the selected activity will start")

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        link = await self.cog.bot.togetherControl.create_link(response.options.voice_channel.id, str(response.options.activities))
        await response.send_message(f"Click the blue link!\n{link}")


class ActivitiesCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Activities(self))

def setup(bot):
    bot.add_cog(ActivitiesCog(bot))