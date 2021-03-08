import discord
from discord.ext import commands

class MySupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='Generates my invite link for your server')
    async def inviteme(self, ctx):
        embed=discord.Embed(title='**Invite Link**',description=f'[My Invite Link!](https://discord.com/oauth2/authorize?client_id=779559821162315787&permissions=2147483656&scope=bot)')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(description='Generates my support server invite')
    async def supportserver(self, ctx):
        await ctx.send('**Here you go, my support server invite**')
        await ctx.send('https://discord.gg/g9zQbjE73K')

def setup(bot):
    bot.add_cog(MySupport(bot))
