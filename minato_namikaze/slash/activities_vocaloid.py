import typing
import discord

from discord.abc import GuildChannel
from discord import application_command_option, VoiceChannel
from lib.functions import meek_api

class Activities(discord.SlashCommand):
    """Get access to discord beta activities feature"""

    activities: typing.Literal[
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
        "checkers"
        ] = discord.application_command_option(
            description="The type of activity",
            default="youtube",
    )

    voice_channel: GuildChannel = application_command_option(channel_types=[VoiceChannel],description="A voice channel in the selected activity will start", name="channel")

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        link = await self.cog.bot.togetherControl.create_link(response.options.channel.id, str(response.options.activities))
        await response.send_message(f"Click the blue link!\n{link}")

class Vocaloids(discord.SlashCommand):
    '''Get kawaii pictures of different vocaloids'''
    vocaloid: typing.Optional[typing.Literal[
        "rin",
        "una",
        "gumi",
        "ia",
        "luka",
        "fukase",
        "miku",
        "len",
        "kaito",
        "teto",
        "meiko",
        "yukari",
        "miki",
        "lily",
        "mayu",
        "aoki",
        "zola",
        "diva"
    ]] = discord.application_command_option(
            description="Select you favourite vocaloid",
            default="miku",
    )

    def __init__(self, cog):
        self.cog = cog

    @staticmethod
    async def callback(response: discord.SlashCommandResponse):
        await response.send_message(embed=await meek_api(response.options.vocaloid))


class ActivitiesCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Activities(self))
        self.add_application_command(Vocaloids(self))

def setup(bot):
    bot.add_cog(ActivitiesCog(bot))