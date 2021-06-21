import statcord
from discord.ext import commands
from ..lib import statcord as statcordkey

class StatcordPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = statcordkey
        self.api = statcord.Client(self.bot, self.key)
        self.api.start_loop()

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.api.command_run(ctx)


def setup(bot):
    bot.add_cog(StatcordPost(bot))
