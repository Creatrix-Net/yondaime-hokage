import discord
from discord.ext import commands
from ...lib import Embed


class BotEventsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            e1 = Embed(title="Command Error!",
                               description=f"`{error}`")
            e1.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e1, delete_after=3)

        elif isinstance(error, commands.MissingPermissions):
            e3 = Embed(title="Command Error!",
                               description=f"`{error}`")
            e3.set_footer(text=f"{ctx.author.name}")
            await ctx.send(embed=e3, delete_after=3)

        elif isinstance(error, commands.MissingRequiredArgument):
            e4 = Embed(title="Command Error!",
                               description=f"`{error}`")
            e4.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e4, delete_after=2)

        elif isinstance(error, commands.CommandNotFound):
            e2 = Embed(title="Command Error!",
                               description=f"`{error}`")
            e2.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e2, delete_after=3)

        elif isinstance(error, commands.CommandInvokeError):
            e7 = Embed(
                title="Oh no, I guess I have not been given proper access! Or some internal error", description=f"`{error}`")
            e7.add_field(name="Command Error Caused By:",
                         value=f"{ctx.command}")
            e7.add_field(name="By", value=f"{ctx.author.name}")
            e7.set_thumbnail(url=f"https://i.imgur.com/1zey3je.jpg")
            e7.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e7, delete_after=5)

        else:
            c = self.bot.get_channel(830366314761420821)

            haaha = ctx.author.avatar_url
            e9 = discord.Embed(
                title="Oh no there was some error", description=f"`{error}`")
            e9.add_field(name="**Command Error Caused By**",
                         value=f"{ctx.command}")
            e9.add_field(
                name="**By**", value=f"**ID** : {ctx.author.id}, **Name** : {ctx.author.name}")
            e9.set_thumbnail(url=f"{haaha}")
            e9.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e9, delete_after=2)
            await c.send(embed=e9)

            await ctx.send('**Sending the error report info to my developer**', delete_after=2)
            e = discord.Embed(
                title=f'In **{ctx.guild.name}**', description=f'User affected {ctx.message.author}')
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner_url_as(format="png"))
            e.add_field(name='**Total Members**', value=ctx.guild.member_count)
            e.add_field(
                name='**Bots**', value=sum(1 for member in ctx.guild.members if member.bot))
            e.add_field(name="**Region**",
                        value=str(ctx.guild.region).capitalize(), inline=True)
            e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            await ctx.send('**Error report was successfully sent**', delete_after=2)
            await c.send(embed=e)


def setup(bot):
    bot.add_cog(BotEventsCommands(bot))
