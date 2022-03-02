import random
from typing import List, Union
from DiscordUtils import Embed, ErrorEmbed
import aiohttp
import discord
import orjson
from discord.ext import commands
from lib import (Characters, LinksAndVars, MemberID,
                 ShinobiMatchCharacterSelection, cache, MatchHandlerView)


class ShinobiMatchCog(commands.Cog, name='Shinobi Match'):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'An amazing shinobi match with your friends'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="dagger")
    
    @staticmethod
    @cache()
    async def characters_data(ctx:commands.Context) -> List[Characters]:
        async with aiohttp.ClientSession() as session:
            async with session.get(LinksAndVars.character_data.value) as resp:
                character_data: dict = orjson.loads(await resp.text())
        return [Characters.from_record(character_data[i], ctx, i) for i in character_data]
    
    @classmethod
    async def return_random_characters(self, ctx:commands.Context) -> List[Characters]:
        characters_data = await self.characters_data(ctx)
        random.shuffle(characters_data)
        return random.sample(characters_data, 25)
    
    @staticmethod
    def return_select_help_embed(author: discord.Member):
        embed= Embed(
            title='Select your character', 
            description='```\nSelect your character using which you will fight\n```\n Use to `dropdown` below to view the characters available and click the `confirm` button to confirm your character'
        )
        embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
        return embed
    
    @commands.command(usage='<opponent.mention>')
    async def match(self, ctx:commands.Context, opponent: Union[discord.Member, MemberID]):
        '''Play shinobi match with your friends using the characters from `Naruto Verse`'''
        view1=ShinobiMatchCharacterSelection(characters_data=await self.return_random_characters(ctx), player=ctx.author, ctx=ctx)
        await ctx.send(embed=self.return_select_help_embed(ctx.author), view=view1) 

        view2=ShinobiMatchCharacterSelection(characters_data=await self.return_random_characters(ctx), player=opponent, ctx=ctx)
        await ctx.send(embed=self.return_select_help_embed(ctx.author), view=view1) 
        
        await view1.wait()
        await view2.wait()

        if view1.character is None or view2.character is None: 
            return ctx.send(embed=ErrorEmbed(title="One of the shinobi didn't choose his character on time."))

def setup(bot):
    bot.add_cog(ShinobiMatchCog(bot))
