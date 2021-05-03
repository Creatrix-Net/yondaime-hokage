import discord
from discord import embeds
from discord.ext import commands
from requests import status_codes
from ...lib.util.utils_dis import *
from ...lib.topgg import *
import requests


class VoteInfo(commands.Cog):
    def __init__(self, bot):
        self.description = 'Get information about your votes for me'
        self.bot = bot
        self.discord_id = bot.discord_id
        
        self.topken = bot.topken
        self.bfd = bot.bfd
        
        self.topgg_site = '[Click Here](https://top.gg/bot/779559821162315787)'
        self.bfd_site = '[Click Here](https://botsfordiscord.com/bot/779559821162315787)'
        self.discordboats_site = '[Click Here](https://discord.boats/bot/779559821162315787/)'
        self.void_bots_site = '[Click Here](https://voidbots.net/bot/779559821162315787/)'
        self.fateslist_bots_site = '[Click Here](https://fateslist.xyz/minato/)'
        self.bladebot_bots_site = '[Click Here](https://bladebotlist.xyz/bot/779559821162315787/)'
        
        self.dblpy = DBLClient(self.bot, self.bot.topken)
        
        
    @commands.command()
    async def vote(self, ctx):
        '''Get all the voting links'''
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)
    
    @commands.command(usage='<member.mention> optional')
    async def hasvoted(self, ctx, member: discord.Member = None):
        '''Check if the user has voted or not'''
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
            e1 = requests.get(f'http://api.voidbots.net/bot/voted/{self.bot.discord_id}/{member.id}',
                            headers={"Authorization": self.bot.voidbot}
                            )
            f = requests.get(f'https://fateslist.xyz/api/v2/bots/{self.bot.discord_id}/votes',
                            headers={"Authorization": self.bot.fateslist},
                            params={'user_id': member.id}
                            )
            g = requests.get(f'https://bladebotlist.xyz/api/bots/{self.bot.discord_id}/votes/{member.id}',
                            )
            c_list = True if str(member.id) in c.json().get('hasVoted24', False) else False
            d_list = d.json().get('voted', False)
            e12 = e1.json().get('voted', False)
            f1 = f.json().get('voted', False)
            g1 = g.json().get('voted', False)
            
            e.add_field(name='**TopGG**', value='Voted : ' + self.topgg_site if await self.dblpy.get_user_vote(member.id) else 'Not Voted : '+ self.topgg_site)
            e.add_field(name='**BotsForDiscord**', value='Voted : ' + self.bfd_site if c_list else 'Not Voted : '+ self.bfd_site)
            e.add_field(name='**DiscordBoats**', value='Voted : ' + self.discordboats_site if d_list else 'Not Voted : '+ self.discordboats_site)
            e.add_field(name='**Void Bots**', value='Voted : ' + self.void_bots_site if e12 else 'Not Voted : '+ self.void_bots_site)
            e.add_field(name='**Fates List**', value='Voted : ' + self.fateslist_bots_site if f1 else 'Not Voted : '+ self.fateslist_bots_site)
            e.add_field(name='**BladeBotList**', value='Voted : ' + self.bladebot_bots_site if g1 else 'Not Voted : '+ self.bladebot_bots_site)
            
            await ctx.send(embed=e)
        
            
    

def setup(bot):
    bot.add_cog(VoteInfo(bot))
