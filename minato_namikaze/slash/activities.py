import typing

import discord

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


class Activities(
        discord.SlashCommand,
        guild_ids=[920536143244709889, 922006581334405180, 920190307595874304],
):
    """Get access to discord beta activities feature"""

    activities: typing.Optional[typing.Literal[
        "youtube", "poker", "chess", "betrayal", "fishing", "letter-league",
        "word-snack", "sketch-heads", "spellcast", "awkword",
        "checkers", ]] = discord.application_command_option(
            description="The type of activity",
            default="youtube",
    )

    @activities.autocomplete
    async def activities_autocomplete(
            self, response: discord.AutocompleteResponse
    ) -> typing.AsyncIterator[str]:
        for activity in activities:
            if response.value.lower() in activity.lower():
                yield activity

    voice_channel: typing.Optional[
        discord.VoiceChannel] = discord.application_command_option(
            description="A voice channel in the selected activity will start")

    @voice_channel.autocomplete
    async def voice_channel_autocomplete(
        self, response: discord.AutocompleteResponse
    ) -> typing.AsyncIterator[discord.VoiceChannel]:
        voice_channel_lists = response.interaction.user.guild.voice_channels
        for voice_channel in voice_channel_lists:
            if response.value.id in voice_channel.id:
                yield voice_channel

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        await response.send_message("Hello", ephemeral=True)


class ActivitiesCog(discord.Cog):
    def __init__(self):
        self.add_application_command(Activities(self))


def setup(bot):
    bot.add_cog(ActivitiesCog())
