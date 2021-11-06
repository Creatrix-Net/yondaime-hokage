import discord
from discord.ext import commands
from discord_together import DiscordTogether

from ..lib import check_if_user_joined_a_channel, ErrorEmbed


class Activites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Allows you access the Discord Activities Beta"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f973")

def setup(bot):
    bot.add_cog(Activites(bot))
