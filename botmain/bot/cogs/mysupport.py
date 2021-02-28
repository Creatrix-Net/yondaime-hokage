import discord
from discord.ext import commands
from requests_oauthlib import OAuth2Session

class MySupport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='Generates my invite link for your server')
    async def inviteme(self, ctx):
        link = OAuth2Session(
            client_id = self.bot.discord_id,
            auto_refresh_kwargs={
                'client_id': self.bot.discord_id,
                'client_secret': self.bot.secrect_client,
                'permissions': 2147483656
            },
            redirect_uri = 'https://dhruvacube.github.io/yondaime-hokage/',
            scope=['bot',],
        )
        url, state = link.authorization_url('https://discord.com/api/v8' + '/oauth2/authorize')
        embed=discord.Embed(title='**Invite Link**',description=f'[My Invite Link!]({url})')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def supportserver(self, ctx):
        embed=discord.Embed(title='**Invite Link**',description=f'[My Invite Link!]({url})')
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(InviteMe(bot))
