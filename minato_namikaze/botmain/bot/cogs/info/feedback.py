import discord
from discord.ext import commands
from discord.ext.commands import command
from ...lib import Embed, return_feedback_channel, ErrorEmbed, check_if_feedback_system_setup


class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Sends your feedback about the server to the server owner. (This can only be done if it is enabled by the server owner)'
    
    @command()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.guild_only()
    @commands.check(check_if_feedback_system_setup)
    async def feedback(self, ctx, *, feed):
        '''Sends your feedback about the server to the server owner. (This can only be done if it is enabled by the server owner)'''
        
        channel = return_feedback_channel(ctx)
        
        e = discord.Embed(title="Feedback sent!",
                description=f"Your feedback '{feed}' has been sent!")
        await ctx.send(embed=e)
        e2 = discord.Embed(
                title=f"{ctx.author} has sent feedback", description=f"{feed}")
        await channel.send(embed=e2)
    
    
    @feedback.error
    async def feedback_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            e = ErrorEmbed(
                title='No Feedback system setup for this server!',
                description='An admin can always setup the **feedback system** using `)setup` command'
            )
            await ctx.send(embed=e, delete_after=10)

def setup(bot):
    bot.add_cog(Feedback(bot))
