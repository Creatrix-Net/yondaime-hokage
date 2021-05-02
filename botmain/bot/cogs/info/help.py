import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Displays the support command for the server, this can onnly be used if the server owner has enabled it.'

    @commands.command(description='Open support ticket if enabled by the server admins')
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def support(self, ctx):
        '''Open support ticket if enabled by the server admins'''
        category = discord.utils.get(ctx.guild.categories, name="Admin / Feedback") if discord.utils.get(ctx.guild.categories, name="Admin / Feedback") else False
        if category:
            chan = discord.utils.get(category.channels, name="support") if discord.utils.get(category.channels, name="support") else False
        else:
            chan = False
        
        if category and chan:
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
        else:
            await ctx.send(f'**Sorry to say** {ctx.author.mention}, but **no support channel** has been setup for the {ctx.guild.name} by the admin! **So, I can\'t help you**')
    
    @commands.command(description='Resolves the existing ticket!',usage='<member.mention>')
    @commands.has_permissions(administrator=True)
    async def resolved(self, ctx, member: discord.Member):
        '''Resolves the existing ticket!'''
        await member.send(f'Hope your issue has been resolved in {ctx.guild.name}, {member.mention}')
        await ctx.send(f'The issue/query for {member.mention} has been set to resolved!')
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="Support_Required"))


def setup(bot):
    bot.add_cog(Help(bot))
