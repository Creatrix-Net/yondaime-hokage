import random
from os.path import join
from pathlib import Path
from .vars import *
from ..classes.embed import Embed
import discord
import aiohttp


class PostStats:
    def __init__(self, bot):
        self.bot = bot

    async def post(self,url, headers, data: dict = None, json: dict = None):
        session = aiohttp.ClientSession()
        request_made = await session.post(url, headers=headers, json=data or json)
        await session.close()
        return request_made

    async def post_guild_stats_all(self):
        guildsno = len(self.bot.guilds)
        members = len(set(self.bot.get_all_members()))

        imageslistdir = Path(__file__).resolve(
            strict=True).parent.parent / join('text','images_list.txt')
        filepointer = open(imageslistdir)
        imageslist = filepointer.readlines()

        a = await self.post(f'https://top.gg/api/bots/{discord_id}/stats',
                            headers={'Authorization': topken},
                            data={'server_count': guildsno}
                            )
        b = await self.post(f'https://discordbotlist.com/api/v1/bots/{discord_id}/stats',
                            headers={'Authorization': dblst},
                            data={'guilds': guildsno, 'users': members}
                            )
        c = await self.post(f'https://botsfordiscord.com/api/bot/{discord_id}',
                            headers={'Authorization': bfd,
                                     'Content-Type': 'application/json'},
                            json={'server_count': guildsno}
                            )
        d = await self.post(f'https://api.botlist.space/v1/bots/{discord_id}',
                            headers={'Authorization': botlist,
                                     'Content-Type': 'application/json'},
                            json={'server_count': guildsno}
                            )
        e = await self.post(f'https://discord.boats/api/bot/{discord_id}',
                            headers={'Authorization': discordboats},
                            data={'server_count': guildsno}
                            )
        f = await self.post(f'https://discord.bots.gg/api/v1/bots/{discord_id}/stats',
                            headers={'Authorization': discordbotsgg,
                                     'Content-Type': 'application/json'},
                            json={'guildCount': guildsno}
                            )
        h = await self.post(f'https://space-bot-list.xyz/api/bots/{discord_id}',
                            headers={"Authorization": spacebot,
                                     "Content-Type": "application/json"},
                            json={"guilds": guildsno, "users": members})

        i = await self.post(f'https://api.voidbots.net/bot/stats/{discord_id}',
                            headers={"Authorization": voidbot,
                                     "Content-Type": "application/json"},
                            json={"server_count": guildsno})
        j = await self.post(f'https://fateslist.xyz/api/v2/bots/{discord_id}/stats',
                            headers={"Authorization": fateslist,
                                     "Content-Type": "application/json"},
                            json={"guild_count": guildsno, "user_count": members})
        k = await self.post(f'https://bladebotlist.xyz/api/bots/{discord_id}/stats',
                            headers={"Authorization": bladebot,
                                     "Content-Type": "application/json"},
                            json={"servercount": guildsno})

        r = self.bot.get_channel(822472454030229545)
        e1 = Embed(title='Status posted successfully',
                           description=f'[Widgets Link]({website}widgets) [Invite Stats](https://minatonamikaze-invites.herokuapp.com/)')
        e1.set_image(url=random.choice(imageslist).strip('\n'))
        e1.set_thumbnail(url=self.bot.user.avatar_url)
        e1.add_field(
            name='TopGG', value=f'{a.status} : [TopGG](https://top.gg/bot/{discord_id})')
        e1.add_field(name='DiscordBotList', value=str(b.status) +
                     ' : [DiscordBotList](https://discord.ly/hatsune-miku)')
        e1.add_field(name='BotsForDiscord', value=str(
            c.status)+f' : [BotsForDiscord](https://botsfordiscord.com/bot/{discord_id})')
        e1.add_field(name='DiscordListSpace', value=str(
            d.status)+f' : [DiscordListSpace](https://discordlist.space/bot/{discord_id})')
        e1.add_field(name='DiscordBoats', value=str(
            e.status)+f' : [DiscordBoats](https://discord.boats/bot/{discord_id})')
        e1.add_field(name='DiscordBots', value=str(
            f.status)+f' : [DiscordBots](https://discord.bots.gg/bots/{discord_id}/)')

        e1.add_field(name='Space Bots', value=str(
            h.status)+f' : [Space Bots](https://space-bot-list.xyz/bots/{discord_id})')

        e1.add_field(name='Void Bots', value=str(
            i.status)+f' : [Void Bots](https://voidbots.net/bot/{discord_id}/)')
        e1.add_field(name='Fates List', value=str(
            j.status)+f' : [Fates List](https://fateslist.xyz/hatsune-miku/)')
        e1.add_field(name='BladeBotList', value=str(
            k.status)+f' : [BladeBotList](https://bladebotlist.xyz/bot/{discord_id}/)')
        
        await r.send(embed=e1)