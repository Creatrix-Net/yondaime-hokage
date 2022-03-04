from typing import List

import aiohttp
import discord
from DiscordUtils import StarboardEmbed
from lib import Webhooks, Database
import typing

class FeedbackModal(discord.ui.Modal):
    children: List[discord.ui.InputText]

    def __init__(self):
        children: List[discord.ui.Item] = [
            discord.ui.InputText(
                label='Your suggestion(s)/feedback or report',
                style=discord.InputTextStyle.paragraph,
                required=True,
                min_length=20,
                placeholder='Type in your suggestions/feedback or report'
            ),
        ]

        super().__init__(title='Feedback / Suggestions / Report', children=children)

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = StarboardEmbed(title='Feedback / Suggestions / Report', description=self.children[0].value)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f'{interaction.guild.name} [{interaction.guild_id}]')
        embed.timestamp = discord.utils.utcnow()
        async with aiohttp.ClientSession() as session:  
            wh = discord.Webhook.from_url(Webhooks.feedback.value, session=session)
            await wh.send(embed=embed)
        await interaction.response.send_message('Your message was successfully sent to my developer', ephemeral=True)

class Feedback(discord.SlashCommand):
    '''Send feedback, suggestion or report regarding me to my developer'''

    def __init__(self, cog):
        self.cog = cog

    async def callback(self,response: discord.SlashCommandResponse):
        await response.send_modal(FeedbackModal())


class Blacklist(discord.SlashCommand):
    '''Some developer releated secret commands'''
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse):
        if await self.client.is_owner(response.user):
            return True
        else:
            await response.send_message("Sorry! but only developer can use this", ephemeral=True)
            return False

class Add(discord.SlashCommand, parent=Blacklist, group=True):
    '''Adds user or guild to the blacklist'''

class User(discord.SlashCommand, parent=Add):
    '''Adds user to the blacklist'''
    user: typing.Union[discord.Member, discord.User, discord.abc.Snowflake] = discord.application_command_option(description="The user to add to the blacklist", default=None)

    async def callback(self, interaction: discord.Interaction) -> None:
        pass

class DeveloperCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Feedback(self))
    
    async def database_class_user(self):
        return await self.bot.db.new(Database.database_category_name.value,Database.database_channel_name.value)

    async def database_class_user(self):
        return await self.bot.db.new(Database.database_category_name.value,Database.antiraid_channel_name.value)

def setup(bot):
    bot.add_cog(DeveloperCog(bot))
