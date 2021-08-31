import discord
from discord.ext import commands
from discord.ext.commands import command

from ...lib import (Embed, ErrorEmbed, check_if_feedback_system_setup,
                    return_feedback_channel)


class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Sends your feedback about the server to the server owner. (This can only be done if it is enabled by the server owner)'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{MEMO}')

    @command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.guild_only()
    @commands.check(check_if_feedback_system_setup)
    async def feedback(self, ctx, *, feed):
        '''Sends your feedback about the server to the server owner. (This can only be done if it is enabled by the server owner)'''
        await ctx.message.delete()
        channel = return_feedback_channel(ctx)

        e = Embed(
            title="Feedback sent!",
            description=f"Your feedback '{feed}' has been sent!",
        )
        await ctx.send(embed=e, delete_after=10)

        e2 = discord.Embed(
            title=f"{ctx.author} has sent feedback", description=f"{feed}",
            colour=ctx.author.color or ctx.author.top_role.colour.value or discord.Color.random()
        )
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
