import random
from os.path import join
from pathlib import Path

from dbl import *
import discord
import requests


class PostStats:
    def __init__(self, bot):
        self.bot = bot

    async def post_guild_stats_all(self):
        guildsno = len(self.bot.guilds)+1
        members = len(set(self.bot.get_all_members()))
        imageslistdir = Path(__file__).resolve(
            strict=True).parent.parent.parent / join( 'images_list.txt')
        filepointer = open(imageslistdir)
        imageslist = filepointer.readlines()

        dblpy = DBLClient(self.bot, self.bot.topken)
        await dblpy.post_guild_count(guildsno)
        b = requests.post(f'https://discordbotlist.com/api/v1/bots/{self.bot.discord_id}/stats',
                          headers={'Authorization': self.bot.dblst},
                          data={'guilds': guildsno, 'users': members}
                          )
        c = requests.post(f'https://botsfordiscord.com/api/bot/{self.bot.discord_id}',
                          headers={'Authorization': self.bot.bfd,
                                   'Content-Type': 'application/json'},
                          json={'server_count': guildsno}
                          )
        d = requests.post(f'https://api.botlist.space/v1/bots/{self.bot.discord_id}',
                          headers={'Authorization': self.bot.botlist,
                                   'Content-Type': 'application/json'},
                          json={'server_count': guildsno}
                          )
        e = requests.post(f'https://discord.boats/api/bot/{self.bot.discord_id}',
                          headers={'Authorization': self.bot.discordboats},
                          data={'server_count': guildsno}
                          )
        f = requests.post(f'https://discord.bots.gg/api/v1/bots/{self.bot.discord_id}/stats',
                          headers={'Authorization': self.bot.discordbotsgg,
                                   'Content-Type': 'application/json'},
                          json={'guildCount': guildsno}
                          )

        h = requests.post(f'https://space-bot-list.xyz/api/bots/{self.bot.discord_id}',
                          headers={"Authorization": self.bot.spacebot,
                                   "Content-Type": "application/json"},
                          json={"guilds": guildsno, "users": members})
        i = requests.post(f'https://api.voidbots.net/bot/stats/{self.bot.discord_id}',
                          headers={"Authorization": self.bot.voidbot,
                                   "Content-Type": "application/json"},
                          json={"server_count": guildsno})
        j = requests.post(f'https://fateslist.xyz/api/v2/bots/{self.bot.discord_id}/stats',
                          headers={"Authorization": self.bot.fateslist,
                                   "Content-Type": "application/json"},
                          json={"guild_count": guildsno, "user_count": members})
        k = requests.post(f'https://bladebotlist.xyz/api/bots/{self.bot.discord_id}/stats',
                          headers={"Authorization": self.bot.bladebot,
                                   "Content-Type": "application/json"},
                          json={"servercount": guildsno})

        r = self.bot.get_channel(822472454030229545)
        e1 = discord.Embed(title='Status posted successfully',
                           description='[Widgets Link](https://the-4th-hokage.github.io/widgets) [Invite Stats](https://minatonamikaze-invites.herokuapp.com/)', color=discord.Color.random())
        e1.set_image(url=random.choice(imageslist).strip('\n'))
        e1.set_thumbnail(url='https://i.imgur.com/Reopagp.jpg')
        e1.add_field(
            name='TopGG', value='200 : [TopGG](https://top.gg/bot/779559821162315787)')
        e1.add_field(name='DiscordBotList', value=str(b.status_code) +
                     ' : [DiscordBotList](https://discord.ly/minato-namikaze)')
        e1.add_field(name='BotsForDiscord', value=str(
            c.status_code)+' : [BotsForDiscord](https://botsfordiscord.com/bot/779559821162315787)')
        e1.add_field(name='DiscordListSpace', value=str(
            d.status_code)+' : [DiscordListSpace](https://discordlist.space/bot/779559821162315787)')
        e1.add_field(name='DiscordBoats', value=str(
            e.status_code)+' : [DiscordBoats](https://discord.boats/bot/779559821162315787)')
        e1.add_field(name='DiscordBots', value=str(
            f.status_code)+' : [DiscordBots](https://discord.bots.gg/bots/779559821162315787/)')
        e1.add_field(name='Space Bots', value=str(
            h.status_code)+' : [Space Bots](https://space-bot-list.xyz/bots/779559821162315787)')
        e1.add_field(name='Void Bots', value=str(
            i.status_code)+' : [Void Bots](https://voidbots.net/bot/779559821162315787/)')
        e1.add_field(name='Fates List', value=str(
            j.status_code)+' : [Fates List](https://fateslist.xyz/minato/)')
        e1.add_field(name='BladeBotList', value=str(
            k.status_code)+' : [BladeBotList](https://bladebotlist.xyz/bot/779559821162315787/)')
        await r.send(embed=e1)
