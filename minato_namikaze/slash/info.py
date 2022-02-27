import discord
from lib import serverinfo, userinfo
from DiscordUtils import Embed

class Server(discord.SlashCommand):
    '''Some server releated commands'''
    def __init__(self, cog):
        self.cog = cog

class Info(discord.SlashCommand, parent=Server):
    '''Shows some basic server info'''
    async def callback(self, response: discord.SlashCommandResponse):
        await response.send_message(embed=await serverinfo(response.interaction.guild, response.interaction.user, self.parent.cog.bot))

class Banner(discord.SlashCommand, parent=Server):
    '''Shows server banner, if there is any'''
    async def callback(self,response: discord.SlashCommandResponse):
        if not response.interaction.guild.banner:
            return await response.send_message("This server does not have a banner...", ephemeral=True)
        e = Embed(title=f":information_source: Banner for {response.interaction.guild}")
        e.set_image(url=response.interaction.guild.banner.with_format("png").url)
        await response.send_message(embed=e)

class Icon(discord.SlashCommand, parent=Server):
    '''Shows server icon, if there is any'''
    async def callback(self,response: discord.SlashCommandResponse):
        if not response.interaction.guild.icon:
            return await response.send_message("This server does not have a avatar...", ephemeral=True)
        e = Embed(title=f":information_source: Icon for {response.interaction.guild}")
        e.set_image(url=response.interaction.guild.icon.with_format("png").url)
        await response.send_message(embed=e)


class UserInfo(discord.UserCommand, name="Info"):
    '''Get some basic user info'''
    def __init__(self, cog):
        self.cog = cog
    
    async def callback(self, response: discord.UserCommandResponse):
        await response.send_message(embed=await userinfo(response.target, response.target.guild, self.parent.cog.bot))


class UserInfoSlash(discord.SlashCommand, name="user"):
    """Get some basic user info"""

    user: discord.Member = discord.application_command_option(description="user")

    def __init__(self, cog):
        self.cog = cog
    
    async def callback(self, response: discord.SlashCommandResponse):
        await response.send_message(embed=await userinfo(response.options.user, response.interaction.guild, self.cog.bot))


class InfoCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Server(self))
        self.add_application_command(UserInfo(self))
        self.add_application_command(UserInfoSlash(self))

def setup(bot):
    bot.add_cog(InfoCog(bot))