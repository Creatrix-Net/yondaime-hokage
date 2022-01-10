import typing

import discord

from ..lib import meek_api


class VocaloidSlash(discord.SlashCommand):
    """Get kawaii Vocaloids photo"""

    def __init__(self, cog):
        self.cog = cog

    vocaloid: typing.Literal["Aoki", "Diva", "Fukase", "Gumi", "Ia", "Kaito",
                             "Len", "Lily", "Luka", "Mayu", "Meiko", "Miki",
                             "Miku", "Rin", "Teto", "Una", "Yukari",
                             "Zola", ] = discord.application_command_option(
                                 description="Vocaloids Name",
                                 default="Miku",
    )

    async def callback(self, response: discord.SlashCommandResponse):
        photo = meek_api(response.options.vocaloid)
        await response.send_message(embed=photo)


class VocaloidSlashCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_user = None
        self.add_application_command(VocaloidSlash(self))


def setup(bot):
    bot.add_cog(VocaloidSlashCog(bot))
