# Discord Imports
import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def support(self, ctx):
        chan = discord.utils.get(ctx.guild.channels, name="support")
        if ctx.message.author == ctx.guild.owner:
            await ctx.send(f'{ctx.message.author.mention} really you need support ??! **LOL !** :rofl:')
        elif discord.utils.get(ctx.guild.roles, name="Support_Required") in ctx.message.author.roles:
            await ctx.send(f'{ctx.author.mention} you already applied for the support , please check the {chan.mention} channel.')
        else:
            channel = ctx.channel
            await ctx.message.author.add_roles(discord.utils.get(ctx.guild.roles, name="Support_Required"))
            if channel.guild is ctx.guild:
                per = ctx.author.mention
                await chan.send(f"{per} in {channel.mention} needs support! @here")
                await ctx.send(f"**Help Desk** has been has been notifed!")
                await ctx.message.author.send(f'Your need for the support in {ctx.guild.name} has been registered')
            else:
                pass
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def resolved(self, ctx, member: discord.Member):
        await member.send(f'Hope your issue has been resolved in {ctx.guild.name}, {member.mention}')
        await ctx.send(f'The issue/query for {member.mention} has been set to resolved!')
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Support_Required"))


def setup(bot):
    bot.add_cog(Help(bot))
