import html
import random
import aiohttp
import discord
from discord.ext import commands

class TriviaView(discord.ui.View):
    def __init__(self, ctx, correct_answer, all_answers):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.correct_answer = correct_answer
        
        for idx, answer in enumerate(all_answers):
            self.add_item(TriviaButton(answer, idx))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This isn't your trivia game!", ephemeral=True)
            return False
        return True
        
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
            if child.label == self.correct_answer:
                child.style = discord.ButtonStyle.success
        
        if hasattr(self, 'message') and self.message:
            embed = self.message.embeds[0]
            embed.color = discord.Color.red()
            embed.set_footer(text="Time's up!")
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.HTTPException:
                pass

class TriviaButton(discord.ui.Button):
    def __init__(self, answer, custom_id_suffix):
        super().__init__(style=discord.ButtonStyle.primary, label=answer[:80], custom_id=f"trivia_{custom_id_suffix}")
        self.answer = answer

    async def callback(self, interaction: discord.Interaction):
        view: TriviaView = self.view
        
        for child in view.children:
            child.disabled = True
            if child.label == view.correct_answer:
                child.style = discord.ButtonStyle.success
            elif child.label == self.label and self.label != view.correct_answer:
                child.style = discord.ButtonStyle.danger
                
        embed = interaction.message.embeds[0]
        
        if self.label == view.correct_answer:
            embed.color = discord.Color.green()
            embed.set_footer(text="Correct!")
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            embed.color = discord.Color.red()
            embed.set_footer(text="Incorrect!")
            await interaction.response.edit_message(embed=embed, view=view)
            
        view.stop()

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Play trivia!"

    @commands.command()
    async def trivia(self, ctx):
        """Start a trivia game."""
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return await ctx.send("Failed to fetch trivia question. Try again later.")
                data = await response.json()
                
        if data.get("response_code") != 0 or not data.get("results"):
            return await ctx.send("Failed to load trivia data.")
            
        result = data["results"][0]
        question = html.unescape(result["question"])
        correct_answer = html.unescape(result["correct_answer"])
        incorrect_answers = [html.unescape(ans) for ans in result["incorrect_answers"]]
        
        all_answers = incorrect_answers + [correct_answer]
        random.shuffle(all_answers)
        
        embed = discord.Embed(
            title="Trivia",
            description=f"**Category:** {result['category']}\n**Difficulty:** {result['difficulty'].capitalize()}\n\n{question}",
            color=discord.Color.blue()
        )
        
        view = TriviaView(ctx, correct_answer, all_answers)
        view.message = await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Trivia(bot))
