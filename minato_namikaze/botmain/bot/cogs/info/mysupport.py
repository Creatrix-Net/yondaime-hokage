import discord
from discord.ext import commands
import platform
import psutil


from ...lib import Embed, get_user


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
        await ctx.send('https://discord.gg/S8kzbBVN8b')
    
    @commands.command(name="stats", description="A usefull command that displays bot statistics.")
    async def stats(self, ctx):
        '''Get the stats for the me'''
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))

        embed = Embed(
            title=f"{self.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.colour or discord.Color.random(),
            timestamp=ctx.message.created_at,
        )

        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(name="**Bot Version:**", value=self.bot.version)
        embed.add_field(name="**Python Version:**", value=pythonVersion)
        embed.add_field(name="**Discord.Py Version**", value=dpyVersion)
        embed.add_field(name="**Total Guilds:**", value=serverCount+1)
        embed.add_field(name="**Total Users:**", value=memberCount)
        embed.add_field(name="**Bot Developers:**",
                        value=f"[{get_user(self.bot.owner_id)}](https://discord.com/users/{self.bot.owner_id}/)")
        embed.add_field(name="**More Info:**",
                        value="[Click Here](https://statcord.com/bot/779559821162315787)")
        embed.add_field(name="**Incidents/Maintenance Reports:**",
                        value="[Click Here](https://minatonamikaze.statuspage.io/)")

        embed.set_footer(text=f"{ctx.author} | {self.bot.user.name}")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar_url)

        await ctx.send(embed=embed)
    
        

def setup(bot):
    bot.add_cog(MySupport(bot))
