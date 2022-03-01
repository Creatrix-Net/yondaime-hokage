import discord
from discord.ext import commands
from typing import List, Union
from lib import Characters, Embed, MemberID
import random

from minato_namikaze.lib.classes.converter import MemberID
class CharacterSelect(discord.ui.Select["ShinobiMatchCharacterSelection"]):
    def __init__(
        self,
        characters: List[Characters],
    ):
        super().__init__(
            placeholder="Select your character...",
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands = commands
        self.characters = characters
        self.__fill_options()

    def __fill_options(self) -> None:
        for i in self.characters:
            self.add_option(
                label=i.name,
                emoji=i.emoji,
                value=i.id
            )

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        value = self.values[0]
        self.view.character = self.view.get_character_config(value)
        await interaction.response.defer()
        embed = Embed(title=self.view.character.name.title())
        embed.set_image(url=random.choice(self.view.character.images))
        embed.set_author(name=self.view.player.display_name,icon_url=self.view.player.display_avatar.url)
        await interaction.message.edit(embed=embed, view=self.view)
        

class ShinobiMatchCharacterSelection(discord.ui.View):
    def __init__(self, characters_data:List[Characters], ctx: commands.Context, player: discord.Member):
        super().__init__()
        self.character = None
        self.ctx = ctx
        self.player = player
        self.add_item(CharacterSelect(characters=characters_data))
    
    def get_character_config(self, character_id: Union[str, int]) -> Characters:
        return discord.utils.get(self.character, id=character_id)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def select(self, button: discord.ui.Button,interaction: discord.Interaction):
        if self.character is None:
            return await interaction.response.send_message('Please select a character before clicking this button', ephemeral=True)
        await interaction.response.defer()
        for i in self.children:
            i.disabled = True
        self.stop()
    
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button,interaction: discord.Interaction):
        await interaction.response.defer()
        for i in self.children:
            i.disabled = True
        self.stop()


class ShinobiMatchCog(commands.Cog, name='Shinobi Match'):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'An amazing shinobi match with your friends'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="dagger")
    
    @commands.command(usage='<opponent.mention>')
    async def match(self, ctx:commands.Context, opponent: Union[discord.Member, MemberID]):
        '''Play shinobi match with your friends using teh characters from `Naruto Verse`'''
        pass 

def setup(bot):
    bot.add_cog(ShinobiMatchCog(bot))