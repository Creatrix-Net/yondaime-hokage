import random
from typing import List, Union, Optional, Tuple

import discord
from discord.ext import commands
from DiscordUtils import Embed
from StringProgressBar import progressBar

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
            await interaction.response.send_message("This `Shinobi match` is not for you", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)


class MatchHandlerViewButton(discord.ui.Button["MatchHandlerView"]):
    def __init__(self, label: str):
        super().__init__(style=discord.ButtonStyle.primary,label=label,row=0)
    
    async def callback(self,interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        view = self.view

class MatchHandlerView(discord.ui.View):
    children: List[MatchHandlerViewButton]
    def __init__(self, player1: Tuple[discord.Member, Characters], player2: Tuple[discord.Member, Characters]):
        super().__init__()
        self.player1: discord.Member = player1[0]
        self.player2: discord.Member = player2[0]

        self.character1: Characters = player1[1]
        self.character2: Characters = player2[1]

        self.turn: discord.Member = self.player1

        self.overall_health: int = 200
        self.health1: int = int(self.overall_health)
        self.health2: int = int(self.overall_health)

        self.special_moves1: int = 2
        self.special_moves2: int = 2

        self.previous_move: Optional[str] = None

        self.special_moves_enery_usage: int = 10 #this is in percentage
        self.button_names: list = ['Kick', 'Punch', 'Ninjutsu Attack', 'Defense', 'Special Power Attack']
        for i in self.button_names:
            self.add_item(MatchHandlerViewButton(label=i))
    
    def percentage_and_progess_bar(self, current_health: int) -> str:
        bardata = progressBar.filledBar(self.overall_health, current_health)
        return f'`{bardata[1]}`\n{bardata[0]}'
    
    def make_embed(self) -> Embed:
        embed = Embed(title='Make your move')
        if self.turn == self.player1:
            embed.set_image(url=random.choice(self.character1.images))
            embed.set_footer(text=f'{self.special_moves1} special moves left')
            embed.description = self.percentage_and_progess_bar(self.health1)
        else:
            embed.set_image(url=random.choice(self.character2.images))
            embed.set_footer(text=f'{self.special_moves2} special moves left')
            embed.description = self.percentage_and_progess_bar(self.health2)
        embed.set_author(name=self.turn.display_name,icon_url=self.turn.display_avatar.url)
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.turn and interaction.user in (self.player1, self.player2):
            await interaction.response.send_message("Please wait for your `turn`", ephemeral=True)
            return False
        if interaction.user != self.turn:
            await interaction.response.send_message("This `Shinobi match` is not for you, please try to be `good spectator`", ephemeral=True)
            return False
        return True