from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_bot_pfp(self):
        url = self.bot.get_guild(
           self.bot.user.avatar_url
        )

        return url  


def setup(bot):
    bot.add_cog(IpcRoutes(bot))