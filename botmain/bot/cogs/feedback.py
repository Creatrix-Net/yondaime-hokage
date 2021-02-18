from discord.ext import commands
import discord
from discord.ext.commands import command

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @command()
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def feedback(self, ctx, *, feed):
        category = discord.utils.get(ctx.guild.categories, name="Admin / Feedback") if discord.utils.get(ctx.guild.categories, name="Admin / Feedback") else False
        if category:
            channel = discord.utils.get(category.channels, name="feedback") if discord.utils.get(category.channels, name="feedback") else False
        else:
            channel = False
        
        if category and channel:
            e = discord.Embed(title="Sent Feedback!",
                            description=f"Your feedback '{feed}' has been sent!")
            await ctx.send(embed=e)
            e2 = discord.Embed(
                title=f"Oh no, is it bad or good? ({ctx.author} has sent feedback)", description=f"{feed}")
            await channel.send(embed=e2)
        else:
            await ctx.send(f'**Sorry to say** {ctx.author.mention}, but **no feedback channel** has been setup for the {ctx.guild.name}')

    @feedback.error
    async def feedback_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            l = self.bot.get_command("feedback")
            left = l.get_cooldown_retry_after(ctx)
            e = discord.Embed(
                title=f"Cooldown left - {round(left)}", color=discord.colour.Color.from_rgb(231, 84, 128))
            await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Feedback(bot))