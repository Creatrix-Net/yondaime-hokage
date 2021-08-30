from ..lib import shinobi_character_channel, humanize_attachments, return_random_5characters, get_user, format_character_name, return_matching_emoji
from typing import Union
from discord_components import Select, SelectOption

import discord
from discord.ext import commands

class Shinobi(commands.Cog, name="Shinobi Match"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Fight like a shinobi with your friends'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{WRESTLERS}')
    
    @commands.command(aliases=["shm", "sh_match", "match", "shinobi"])
    @commands.is_owner()
    async def shinobi_match(self, ctx, member: Union[int, discord.Member]):
        '''Have shinobi match with your friend'''
        member = get_user(member, ctx)
        a=self.bot.get_channel(shinobi_character_channel)
        characters = {}
        async for i in a.history(limit=None,oldest_first=True):
            if characters.get(i.content.lower().strip(' ')):
                characters.update(
                    {
                        i.content.lower().strip(' '): humanize_attachments(characters.get(i.content.lower())+i.attachments)
                    }
                )
            else:
                characters.update(
                    {
                        i.content.lower().strip(' '): humanize_attachments(i.attachments)
                    }
                )
        player_init_5_characters = return_random_5characters(characters)
        player_other_5_characters = return_random_5characters(characters)
        
        player_init_select = [
            Select(
                placeholder='Select your fighter Shinobi',
                max_values=1,
                min_values=1,
                options=[
                    SelectOption(label=format_character_name(i),value=i.lower(),default=False, emoji=return_matching_emoji(ctx, i)) for i in player_init_5_characters
                ]
            )
        ]
        await ctx.send(
            content=ctx.author.mention,
            components=player_init_select
        )
        interaction = await ctx.bot.wait_for("select_option", check = lambda i: i.placeholder == "Select your fighter Shinobi")
        await interaction.respond(content = f"{interaction.component[0].label} selected!")

def setup(bot):
    bot.add_cog(Shinobi(bot))
