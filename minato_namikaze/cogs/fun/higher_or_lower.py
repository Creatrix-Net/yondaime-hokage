from __future__ import annotations
import random
import discord
from discord.ext import commands

class HigherOrLowerView(discord.ui.View):
    def __init__(self, ctx, current_number):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.current_number = current_number
        self.score = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your game!", ephemeral=True)
            return False
        return True

    async def process_guess(self, interaction: discord.Interaction, guess_higher: bool):
        next_number = random.randint(1, 100)
        while next_number == self.current_number:
            next_number = random.randint(1, 100)

        won = (guess_higher and next_number > self.current_number) or (not guess_higher and next_number < self.current_number)

        if won:
            self.score += 1
            self.current_number = next_number
            embed = discord.Embed(
                title="Higher or Lower",
                description=f"Correct! The number was **{next_number}**.\n\nCurrent Score: **{self.score}**\n\nIs the next number (1-100) higher or lower than **{self.current_number}**?",
                color=discord.Color.green(),
            )
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            embed = discord.Embed(
                title="Higher or Lower - Game Over",
                description=f"Wrong! The number was **{next_number}**.\n\nFinal Score: **{self.score}**",
                color=discord.Color.red(),
            )
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
            self.stop()

    @discord.ui.button(label="Higher", style=discord.ButtonStyle.success, emoji="⬆️")
    async def btn_higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_guess(interaction, True)

    @discord.ui.button(label="Lower", style=discord.ButtonStyle.danger, emoji="⬇️")
    async def btn_lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_guess(interaction, False)

class HigherOrLower(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Play higher or lower!"

    @commands.command(aliases=["hol"])
    async def higherorlower(self, ctx):
        """Play a game of Higher or Lower."""
        number = random.randint(1, 100)
        view = HigherOrLowerView(ctx, number)

        embed = discord.Embed(
            title="Higher or Lower",
            description=f"I picked a number between 1 and 100.\n\nIs the next number higher or lower than **{number}**?",
            color=discord.Color.blue(),
        )
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HigherOrLower(bot))
