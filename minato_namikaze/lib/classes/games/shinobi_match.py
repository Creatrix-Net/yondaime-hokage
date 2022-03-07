import asyncio
import random
from typing import List, Optional, Tuple, Union

import discord
from discord.ext import commands
from DiscordUtils import Embed, StarboardEmbed
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
        super().__init__(style=discord.ButtonStyle.primary,label=label.upper(),row=0)
    
    async def callback(self,interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        view = self.view
        if self.label.lower() in ['kick', 'punch']:
            await self.reduce_health(amount=random.randint(1,5))
        elif self.label.lower() == 'Ninjutsu Attack'.lower():
            await self.reduce_health(amount=abs(view.character1.hitpoint - view.character2.regainpoint) if view.turn == view.player1 else abs(view.character2.hitpoint - view.character1.regainpoint))
        elif self.label.lower() == 'Special Power Attack'.lower():
            await self.reduce_health(amount=(view.character1.specialpoint/100)*view.overall_health if view.turn == view.player1 else (view.character2.specialpoint/100)*view.overall_health)
            if view.turn == view.player1:
                view.special_moves1 -=1
                view.health1 -= (view.character1.specialpoint/1000)* view.health1
            else:
                view.special_moves2 -=1
                view.health2 -= (view.character2.specialpoint/1000)* view.health2
            if view.special_moves1 < 0:
                view.special_moves1 = 0
            
            if view.special_moves2 < 0:
                view.special_moves2 = 0
        elif self.label.lower() == 'Heal'.lower():
            health = view.health1 if view.turn == view.player1 else view.health2
            if health < view.overall_health:
                character = view.character1 if view.turn == view.player1 else view.character2
                await self.reduce_health(amount=character.specialpoint, heal=True)
            
                if view.turn == view.player1:
                    view.heal_moves1 -= 1
                else:
                    view.heal_moves2 -= 1
            
            if view.heal_moves1 < 0:
                view.heal_moves1 = 0
            
            if view.heal_moves2 < 0:
                view.heal_moves2 = 0
        
        if view.turn == view.player1:
            view.previous_move1 = self.label
        else:
            view.previous_move2 = self.label
        
        for i in view.children:
            i.disabled = True
        
        winner = await view.determine_winer()
        if winner is not None:
            await interaction.response.defer()
            await interaction.message.edit(content=None, embeds=winner, view=view)
            return view.stop()
        
        await interaction.response.defer()
        await interaction.message.edit(content=f'{view.turn.mention} your stats', embed=view.make_embed(), view=view)
        await asyncio.sleep(2)
        view.turn = view.player2 if view.turn == view.player1 else view.player1
        for i in view.children:
            if view.turn == view.player1:
                if i.label.lower() == 'Special Power Attack'.lower() and view.special_moves1 <= 0:
                    i.disabled = True
                elif i.label.lower() == 'Heal'.lower() and view.heal_moves1 <= 0:
                    i.disabled = True
                elif i.label.lower() == str(view.previous_move1).lower():
                    i.disabled = True
                else:
                    i.disabled = False
            else:
                if i.label.lower() == 'Special Power Attack'.lower() and view.special_moves2 <= 0:
                    i.disabled = True
                elif i.label.lower() == 'Heal'.lower() and view.heal_moves2 <= 0:
                    i.disabled = True
                elif i.label.lower() == str(view.previous_move2).lower():
                    i.disabled = True
                else:
                    i.disabled = False
        
        await interaction.message.edit(content=f'{view.turn.mention} now your turn', embed=view.make_embed(), view=view)

    async def reduce_health(self, amount: int, heal: bool = False) -> None:
        if self.view is None:
            raise AssertionError
        view=self.view
        if not heal:
            if view.turn == view.player1:
                view.health2 -= amount
            else:
                view.health1 -= amount
        else:
            if view.turn == view.player1:
                view.health1 += abs(amount)
            else:
                view.health2 += abs(amount)
        
        if view.health2 < 0:
            view.health2 = 0
        
        if view.health1 < 0:
            view.health1 = 0
        
        if view.health2 > view.overall_health:
            view.health2 = view.overall_health
        
        if view.health1 > view.overall_health:
            view.health1 = view.overall_health

class MatchHandlerView(discord.ui.View):
    children: List[MatchHandlerViewButton]
    def __init__(self, player1: Tuple[discord.Member, Characters], player2: Tuple[discord.Member, Characters], message: Optional[discord.Message] = None):
        super().__init__()
        self.message = message
        self.player1: discord.Member = player1[0]
        self.player2: discord.Member = player2[0]

        self.character1: Characters = player1[1]
        self.character2: Characters = player2[1]

        self.turn: discord.Member = self.player1

        self.overall_health: int = 100
        self.health1: int = int(self.overall_health)
        self.health2: int = int(self.overall_health)

        self.special_moves1: int = 2
        self.special_moves2: int = 2

        self.heal_moves1: int = 2
        self.heal_moves2: int = 2

        self.previous_move1: Optional[str] = None
        self.previous_move2: Optional[str] = None

        self.special_moves_energy_usage: int = 10 #this is in percentage
        self.button_names: list = ['Kick', 'Punch', 'Ninjutsu Attack', 'Heal', 'Special Power Attack']
        for i in self.button_names:
            self.add_item(MatchHandlerViewButton(label=i))
    
    def percentage_and_progess_bar(self, current_health: int) -> str:
        bardata = progressBar.filledBar(self.overall_health, int(current_health))
        return f'`{bardata[1]}%`\n{bardata[0]}'
    
    def make_embed(
        self, 
        character: Optional[Characters] = None, 
        author: Optional[discord.Member] = None,
        color: Optional[discord.Color] = None,
    ) -> Embed:
        character = character or (self.character1 if self.turn == self.player1 else self.character2)
        author = author or (self.player1 if character == self.character1 else self.player2)
        embed = Embed()
        embed.title = character.name
        embed.set_image(url=random.choice(character.images))
        embed.set_footer(text=f'{self.special_moves1 if character == self.character1 else self.special_moves2} special moves left | {self.heal_moves1 if character == self.character1 else self.heal_moves2} heal operations left')
        embed.description = self.percentage_and_progess_bar(self.health1 if character== self.character1 else self.health2)
        embed.set_author(name=author.display_name,icon_url=author.display_avatar.url)
        if color is not None:
            embed.color = color
        return embed
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.turn and interaction.user in (self.player1, self.player2):
            await interaction.response.send_message("Please wait for your `turn`", ephemeral=True)
            return False
        if interaction.user != self.turn:
            await interaction.response.send_message("This `Shinobi match` is not for you, please try to be `good spectator`", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        if self.message is None:
            return
        for i in self.children:
            i.disabled = True
        await self.message.edit(content = None, embeds=await self.determine_winer(force=True), view=self)
        return self.stop()
    
    async def determine_winer(self, force: bool = False) -> Optional[List[discord.Embed]]:
        if not force:
            if self.health1 > 0 and self.health2 > 0:
                return
        
        if self.health1 == self.health2:
            embed = StarboardEmbed(title="No one won the match!")
            embed.description = f'In a fight of `{self.character1.name.title()} vs {self.character2.name.title()}` [{self.player1.mention} `vs` {self.player2.mention}]\n No one won the match'
            embed.timestamp = discord.utils.utcnow()
            return [embed]
        
        if not force:
            winner = self.player1 if self.health1 > 0 else self.player2
            looser = self.player1 if self.health1 <= 0 else self.player2
        else:
            winner = self.player1 if self.health1 > self.health2 else self.player2
            looser = self.player1 if self.health1 < self.health2 else self.player2

        winner_character = self.character1 if winner == self.player1 else self.character2
        looser_character = self.character1 if looser == self.player1 else self.character2
        
        embed = StarboardEmbed(title=f'{winner_character.name.title()} won the match')
        if force:
            embed.title = f'{winner_character.name.title()} won the match, due the timeout'
        embed.description = f'In a fight of `{winner_character.name.title()} vs {looser_character.name.title()}` [{winner.mention} `vs` {looser.mention}]\n `{winner_character.name.title()}` [{winner.mention}] won the match.\n Congratulations! :tada:'
        embed.timestamp = discord.utils.utcnow()
        return [
            embed,
            self.make_embed(character=winner_character, author=winner,color=discord.Color.green()),
            self.make_embed(character=looser_character,author=looser,color=discord.Color.red())
        ]
