import discord
from discord import embeds
from discord.ext import commands
from requests import status_codes
from ...lib.util.utils_dis import *
import topgg, requests


class VoteInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.discord_id = bot.discord_id
        
        self.topken = bot.topken
        self.bfd = bot.bfd
        
        self.topgg_site = '[Click Here](https://top.gg/bot/779559821162315787)'
        self.bfd_site = '[Click Here](https://botsfordiscord.com/bot/779559821162315787)'
        self.discordboats_site = '[Click Here](https://discord.boats/bot/779559821162315787/)'
        
        self.dblpy = topgg.DBLClient(self.bot, self.bot.topken)
        
        
    @commands.command()
    async def vote(self, ctx):
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)
    
    @commands.command()
    async def hasvoted(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author
        async with ctx.channel.typing():
            e = discord.Embed(title=f'{member.display_name} vote stats for me',description=f'{member.mention} here your voting stats for last 12hours', colour=0xf1c40f)
            e.set_thumbnail(url=member.avatar_url)
            
            c = requests.get(f'https://botsfordiscord.com/api/bot/{self.bot.discord_id}/votes',
                            headers={'Authorization': self.bfd,
                                    'Content-Type': 'application/json'},
                            )
            d = requests.get(f'https://discord.boats/api/bot/{self.bot.discord_id}/voted',
                            params={'id': member.id}
            
                            )
            c_list = True if str(member.id) in c.json()['hasVoted24'] else False
            d_list = d.json()['voted']
            
            e.add_field(name='TopGG', value='Voted : ' + self.topgg_site if await self.dblpy.get_user_vote(member.id) else 'Not Voted : '+ self.topgg_site)
            e.add_field(name='BotsForDiscord', value='Voted : ' + self.bfd_site if c_list else 'Not Voted : '+ self.bfd_site)
            e.add_field(name='DiscordBoats', value='Voted : ' + self.discordboats_site if d_list else 'Not Voted : '+ self.discordboats_site)
            
            await ctx.send(embed=e)
        
            
    

def setup(bot):
    bot.add_cog(VoteInfo(bot))