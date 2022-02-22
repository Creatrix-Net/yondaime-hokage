from typing import List, Optional

import discord
from akinator.async_aki import Akinator as _Akinator_

from DiscordUtils import Embed

YES = discord.PartialEmoji(name="\U00002705")
NO = discord.PartialEmoji(name="\U0000274c")
IDK = discord.PartialEmoji(name="\U0001f937")
P = discord.PartialEmoji(name="\U0001f614")
PN = discord.PartialEmoji(name="\U0001f614")
STOP = discord.PartialEmoji(name="\U0001f6d1")


class AkinatorButtons(discord.ui.Button["Akinator"]):
    def __init__(self, emoji: discord.PartialEmoji):
        super().__init__(style=discord.ButtonStyle.secondary,emoji=emoji)
    
    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        view: Akinator = self.view

        await interaction.response.defer()

        if view.aki.progression <= 80:

            if self.emoji == STOP:
                view.stop()
                await interaction.message.delete()
                return 

            view.questions += 1
            await view.aki.answer(view.mapping[self.emoji])
            embed = await view.build_embed()
            await interaction.message.edit(embed=embed, view=view)
            return

        embed = await view.win()
        for child in view.children:
            child.disabled = True
        await interaction.message.edit(embed=embed, view=view)


class Akinator(discord.ui.View):
    children: List[AkinatorButtons]
    def __init__(self):
        super().__init__()
        self.aki = _Akinator_()
        self.bar_emojis: tuple = ("  ", "\U00002588")
        self.guess = None
        self.bar = ""
        self.message: Optional[discord.Message] = None
        self.questions = 0
        self.mapping: dict = {YES: "y", NO: "n", IDK: "i", P: "p", PN: "pn"}

        for i in self.mapping:
            self.add_item(AkinatorButtons(emoji=i))
        self.add_item(AkinatorButtons(emoji=STOP))

    def build_bar(self) -> str:
        prog = round(self.aki.progression / 8)
        emp, full = self.bar_emojis
        self.bar = f"[`{full*prog}{emp*(10-prog)}`]"
        return self.bar

    async def build_embed(self) -> discord.Embed:
        embed = Embed(
            title="Guess your character!",
            description=("```swift\n"
                         f"Question-Number  : {self.questions}\n"
                         f"Progression-Level: {self.aki.progression}\n```\n"
                         f"{self.build_bar()}"),
        )
        embed.add_field(name="- Question -", value=self.aki.question)
        embed.set_footer(
            text="Figuring out the next question | This may take a second")
        return embed

    async def win(self):
        await self.aki.win()
        self.guess = self.aki.first_guess

        embed = discord.Embed()
        embed.title = "Character Guesser Engine Results"
        embed.description = f"Total Questions: `{self.questions}`"
        embed.add_field(
            name="Character Guessed",
            value=f"\n**Name:** {self.guess['name']}\n{self.guess['description']}",
        )
        embed.set_image(url=self.guess["absolute_picture_path"])
        embed.set_footer(text="Was I correct?")

        return embed

    async def start(self):
        await self.aki.start_game(child_mode=True)
    
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)
