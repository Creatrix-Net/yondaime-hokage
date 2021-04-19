from discord.ext import commands, ipc
import discord

class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_bot_pfp(self,data):
        url = str(self.bot.user.avatar_url)
        return url
    
    @ipc.server.route()
    async def get_text_channels(self,data):
        guild = discord.utils.get(self.bot.guilds, id=int(data.guildid))
        text_channel_list = list()
        for channel in guild.text_channels:
            text_channel_list.append(channel)
        return text_channel_list


def setup(bot):
    bot.add_cog(IpcRoutes(bot))