import discord
from discord.ext import commands


class MySupport(commands.Cog, name="My Support"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Having problems with me? Then you can get the help here.'
    
    @commands.command(description='Generates my invite link for your server')
    async def inviteme(self, ctx):
        '''Generates my invite link for your server'''
        embed=discord.Embed(title='**Invite Link**',description=f'[My Invite Link!](https://minatonamikaze-invites.herokuapp.com/invite?sitename=Direct%20From%20Bot&password=cube12345%3F)')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(description='Generates my support server invite')
    async def supportserver(self, ctx):
        '''Generates my support server invite'''
        await ctx.send('**Here you go, my support server invite**')
        await ctx.send('https://discord.gg/g9zQbjE73K')

def setup(bot):
    bot.add_cog(MySupport(bot))
