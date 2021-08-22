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

class Google(discord.ui.View):
    def __init__(self):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus('dhruva shaw')
        url = f'https://www.google.com/search?q={query}'

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))