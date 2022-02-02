import statcord
from discord.ext import commands

from lib import Tokens


class StatcordPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = Tokens.statcord.value
        self.api = statcord.StatcordClient(self.bot, self.key)

    def cog_unload(self):
        self.statcord_client.close()


def setup(bot):
    bot.add_cog(StatcordPost(bot))
