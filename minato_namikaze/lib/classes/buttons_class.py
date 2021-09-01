import discord
from ..util import help_smile_emoji, server_id
from urllib.parse import quote_plus



class SupportServerButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
            
        self.add_item(
                discord.ui.Button(
                    label="Support Server",
                    url="https://discord.gg/S8kzbBVN8b",
            )
        )
