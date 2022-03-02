import random
from typing import List, Union, Optional

import discord
from discord.ext import commands
from DiscordUtils import Embed

from ..converter import Characters

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
    children: List[Union[CharacterSelect, discord.Button, discord.ui.Button]]
    def __init__(self, characters_data:List[Characters], ctx: commands.Context, player: discord.Member, message: Optional[discord.Message] = None):
        super().__init__()
        self.character = None
        self.ctx = ctx
        self.player = player
        self.characters_data = characters_data
        self.message = message
        self.add_item(CharacterSelect(characters=characters_data))
    
    def get_character_config(self, character_id: Union[str, int]) -> Characters:
        return discord.utils.get(self.characters_data, id=character_id)
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green,row=2)
    async def select(self, button: discord.ui.Button,interaction: discord.Interaction):
        if self.character is None:
            return await interaction.response.send_message('Please select a character before clicking this button', ephemeral=True)
        await interaction.response.defer()
        for i in self.children:
            i.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
    
    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red,row=2)
    async def cancel(self, button: discord.ui.Button,interaction: discord.Interaction):
        await interaction.response.defer()
        for i in self.children:
            i.disabled = True
        await interaction.message.edit(view=self)
        self.stop()
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.player:
            await interaction.response.send_message("This `Shinobi` match is not for you", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
