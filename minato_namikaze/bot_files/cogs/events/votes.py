from typing import Optional, Union

import discord
import requests
from discord.ext import commands

from ...lib import *


class VoteInfo(commands.Cog):
    def __init__(self, bot):
        self.description = 'Get information about your votes for me'
        self.bot = bot

        self.topgg_site = f'[Click Here](https://top.gg/bot/{self.bot.user.id})'
        self.bfd_site = f'[Click Here](https://botsfordiscord.com/bot/{self.bot.user.id})'
        self.discordboats_site = f'[Click Here](https://discord.boats/bot/{self.bot.user.id}/)'
        self.void_bots_site = f'[Click Here](https://voidbots.net/bot/{self.bot.user.id}/)'
        self.fateslist_bots_site = '[Click Here](https://fateslist.xyz/minato/)'
        self.bladebot_bots_site = f'[Click Here](https://bladebotlist.xyz/bot/{self.bot.user.id}/)'
        self.discordlistspacesite = f'[Click Here](https://discordlist.space/bot/{self.bot.user.id})'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{BALLOT BOX WITH BALLOT}')

    @commands.command()
    async def vote(self, ctx):
        '''Get all the voting links'''
        m = VotingMenu(bot=self.bot)
        await m.start(ctx)

    @commands.command(usage='<member.mention> optional')
    async def hasvoted(self, ctx, member: Optional[Union[int, discord.Member]] = None):
        '''Check if the user has voted or not'''
        member = get_user(ctx.author if not member else member, ctx)
        if member.bot:
            return await ctx.send('You **can\'t** check for a **bot account**')
        async with ctx.channel.typing():
            e = Embed(
                title=f'{member.display_name} vote stats for me',
                description=f'{member.mention} here your voting stats for last 12hours'
            )
            e.set_thumbnail(url=member.avatar_url)
            a = requests.get(
                f'https://top.gg/api/bots/{self.bot.user.id}/check',
                params={'userId': member.id},
                headers={
                    "Authorization": topken
                }
            )
            c = requests.get(f'https://botsfordiscord.com/api/bot/{self.bot.user.id}/votes',
                             headers={'Authorization': bfd,
                                      'Content-Type': 'application/json'},
                             )
            d = requests.get(f'https://discord.boats/api/bot/{self.bot.user.id}/voted',
                             params={'id': member.id}

                             )
            e1 = requests.get(f'http://api.voidbots.net/bot/voted/{self.bot.user.id}/{member.id}',
                              headers={"Authorization": voidbot}
                              )
            f = requests.get(f'https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/votes',
                             headers={"Authorization": fateslist},
                             params={'user_id': member.id}
                             )
            g = requests.get(f'https://bladebotlist.xyz/api/bots/{self.bot.user.id}/votes/{member.id}',
                             )

            h = requests.get(f'https://api.discordlist.space/v2/bots/{self.bot.user.id}/status/{member.id}',
                             headers={"Authorization": botlist}
                             )

            try:
                a_list = True if a.json().get('voted') >= 1 else False
            except:
                a_list = False

            try:
                c_list = True if str(member.id) in c.json().get(
                    'hasVoted24', False) else False
            except:
                c_list = False

            try:
                d_list = d.json().get('voted', False)
            except:
                d_list = False

            try:
                e12 = e1.json().get('voted', False)
            except:
                e12 = False

            try:
                f1 = f.json().get('voted', False)
            except:
                f1 = False

            try:
                g1 = g.json().get('voted', False)
            except:
                g1 = False

            try:
                h1 = h.json().get('upvoted', False)
            except:
                h1 = False

            e.add_field(
                name='**TopGG**',
                value=f'Voted : {self.topgg_site}' if a_list else f'Not Voted : {self.topgg_site}'
            )
            e.add_field(
                name='**BotsForDiscord**',
                value=f'Voted : {self.bfd_site}' if c_list else f'Not Voted : {self.bfd_site}'
            )
            e.add_field(
                name='**DiscordBoats**',
                value=f'Voted : {self.discordboats_site}' if d_list else f'Not Voted : {self.discordboats_site}'
            )
            e.add_field(
                name='**Void Bots**',
                value=f'Voted : {self.void_bots_site}' if e12 else f'Not Voted : {self.void_bots_site}'
            )
            e.add_field(
                name='**Fates List**',
                value=f'Voted : {self.fateslist_bots_site}' if f1 else f'Not Voted : {self.fateslist_bots_site}'
            )
            e.add_field(
                name='**BladeBotList**',
                value=f'Voted : {self.bladebot_bots_site}' if g1 else f'Not Voted : {self.bladebot_bots_site}'
            )
            e.add_field(
                name='**DiscordListSpace**',
                value=f'Voted : {self.discordlistspacesite}' if g1 else f'Not Voted : {self.discordlistspacesite}'
            )

            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(VoteInfo(bot))
