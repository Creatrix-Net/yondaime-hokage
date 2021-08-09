from ..lib import shinobi_character_channel, humanize_attachments, return_random_5characters, get_user, return_uchiha_emoji, return_senju_emoji
from typing import Union
from discord_components import Select, SelectOption

import discord
from discord.ext import commands

class Shinobi(commands.Cog, name="Shinobi Match"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Fight like a shinobi with your friends'
    
    @commands.command(aliases=["shm", "sh_match", "match", "shinobi"])
    async def shinobi_match(self, ctx, member: Union[int, discord.Member]):
        '''Have shinobi match with your friend'''
        member = get_user(member, ctx)
        a=self.bot.get_channel(shinobi_character_channel)
        characters = {}
        async for i in a.history(limit=None,oldest_first=True):
            if characters.get(i.content.title().strip(' ')):
                characters.update(
                    {
                        i.content.title().strip(' '): humanize_attachments(characters.get(i.content.title())+i.attachments)
                    }
                )
            else:
                characters.update(
                    {
                        i.content.title().strip(' '): humanize_attachments(i.attachments)
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
                    SelectOption(label=i,value=i,default=False, emoji=return_uchiha_emoji(ctx)) for i in player_init_5_characters
                ]
            )
        ]
        await ctx.send(
            content=ctx.author.mention,
            components=player_init_select
        )

def setup(bot):
    bot.add_cog(Shinobi(bot))
