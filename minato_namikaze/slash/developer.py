from typing import List

import aiohttp
import discord
from DiscordUtils import StarboardEmbed
from lib import Webhooks


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

class Feedback(discord.SlashCommand, guild_ids=[920536143244709889, 920190307595874304]):
    '''Send feedback, suggestion or report regarding me to my developer'''

    def __init__(self, cog):
        self.cog = cog

    async def callback(self,response: discord.SlashCommandResponse):
        await response.send_modal(FeedbackModal())

class DeveloperCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Feedback(self))

def setup(bot):
    bot.add_cog(DeveloperCog(bot))
