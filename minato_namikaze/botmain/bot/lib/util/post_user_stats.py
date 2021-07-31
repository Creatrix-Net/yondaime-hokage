import random
from os.path import join
from pathlib import Path
import time

import aiohttp

from ..classes.embed import Embed
from .vars import *

class PostStats:
    def __init__(self, bot):
        self.bot = bot
    
    async def post_commands(self):
        commands_list = []
        for i in self.bot.commands:
            tuple_notes = (i.description.lower(), i.short_doc.lower())
            parameters = list(j for j in i.clean_params)
            dict_append = {
                'cmd_name': i.cog_name,
                'friendly_name': i.qualified_name,
                'description': i.description,
                'cmd_groups': i.parents+[i.cog_name] if i.cog_name else i.parents,
                'examples': [i.usage],
                'cmd_type': 0,
                'notes': ['Vote locked'] if 'vote locked' in tuple_notes or 'votes lock' in tuple_notes or 'vote lock' in tuple_notes else []
            }
            commands_list.append(dict_append)
        for i in commands_list:
            j = await self.post(
                f'https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/commands',
                headers={"Authorization": fateslist,
                "Content-Type": "application/json"},
                json=i
            )
            print(j, j.status)
            time.sleep(0.5)
            

    async def post(self, url, headers, data: dict = None, json: dict = None):
        try:
            session = aiohttp.ClientSession()
            request_made = await session.post(url, headers=headers, json=data or json)
            await session.close()
            return request_made.status
        except:
            return 503

    async def post_guild_stats_all(self):
        guildsno = len(self.bot.guilds)
        members = len(set(self.bot.get_all_members()))

        imageslistdir = Path(__file__).resolve(
            strict=True).parent.parent / join('text', 'images_list.txt')
        filepointer = open(imageslistdir)
        imageslist = filepointer.readlines()

        a = await self.post(f'https://top.gg/api/bots/{self.bot.user.id}/stats',
                            headers={'Authorization': topken},
                            data={'server_count': guildsno}
                            )
        b = await self.post(f'https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats',
                            headers={'Authorization': dblst},
                            data={'guilds': guildsno, 'users': members}
                            )
        c = await self.post(f'https://botsfordiscord.com/api/bot/{self.bot.user.id}',
                            headers={'Authorization': bfd,
                                     'Content-Type': 'application/json'},
                            json={'server_count': guildsno}
                            )
        d = await self.post(f'https://api.discordlist.space/v2/bots/{self.bot.user.id}',
                            headers={'Authorization': f'Bot {botlist}',
                                     'Content-Type': 'application/json'},
                            json={'serverCount': guildsno, 'active': True}
                            )
        e = await self.post(f'https://discord.boats/api/bot/{self.bot.user.id}',
                            headers={'Authorization': discordboats},
                            data={'server_count': guildsno}
                            )
        f = await self.post(f'https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats',
                            headers={'Authorization': discordbotsgg,
                                     'Content-Type': 'application/json'},
                            json={'guildCount': guildsno}
                            )
        h = await self.post(f'https://space-bot-list.xyz/api/bots/{self.bot.user.id}',
                            headers={"Authorization": spacebot,
                                     "Content-Type": "application/json"},
                            json={"guilds": guildsno, "users": members})

        i = await self.post(f'https://api.voidbots.net/bot/stats/{self.bot.user.id}',
                            headers={"Authorization": voidbot,
                                     "Content-Type": "application/json"},
                            json={"server_count": guildsno})
        j = await self.post(f'https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/stats',
                            headers={"Authorization": fateslist,
                                     "Content-Type": "application/json"},
                            json={"guild_count": guildsno, "user_count": members})
        k = await self.post(f'https://bladebotlist.xyz/api/bots/{self.bot.user.id}/stats',
                            headers={"Authorization": bladebot,
                                     "Content-Type": "application/json"},
                            json={"servercount": guildsno})
        l = await self.post(f'https://bots.discordlabs.org/v2/bot/{self.bot.user.id}/stats',
                            headers={"Authorization": discordlabs,
                                     "Content-Type": "application/json"},
                            json={"server_count": guildsno})

        r = self.bot.get_channel(822472454030229545 if not self.bot.local else 870561578347540490)
        e1 = Embed(title='Status posted successfully',
                   description=f'[Widgets Link]({website}widgets) [Invite Stats](https://minatonamikaze-invites.herokuapp.com/)')
        e1.set_image(url=random.choice(imageslist).strip('\n'))
        e1.set_thumbnail(url=self.bot.user.avatar_url)
        
        
        e1.add_field(name='TopGG', value=f'{a} : [TopGG](https://top.gg/bot/{self.bot.user.id})')
        e1.add_field(name='DiscordBotList', value=f'{b} : [DiscordBotList](https://discord.ly/hatsune-miku)')
        e1.add_field(name='BotsForDiscord',value=f'{c} : [BotsForDiscord](https://botsfordiscord.com/bot/{self.bot.user.id})')
        e1.add_field(name='DiscordListSpace', value=f'{d} : [DiscordListSpace](https://discordlist.space/bot/{self.bot.user.id})')
        e1.add_field(name='DiscordBoats', value=f'{e} : [DiscordBoats](https://discord.boats/bot/{self.bot.user.id})')
        e1.add_field(name='DiscordBots', value=f'{f} : [DiscordBots](https://discord.bots.gg/bots/{self.bot.user.id}/)')

        e1.add_field(name='Space Bots', value=f'{h} : [Space Bots](https://space-bot-list.xyz/bots/{self.bot.user.id})')

        e1.add_field(name='Void Bots', value=f'{i} : [Void Bots](https://voidbots.net/bot/{self.bot.user.id}/)')
        e1.add_field(name='Fates List', value=f'{j} : [Fates List](https://fateslist.xyz/minato/)')
        e1.add_field(name='BladeBotList', value=f'{k} : [BladeBotList](https://bladebotlist.xyz/bot/{self.bot.user.id}/)')
        e1.add_field(name='DiscordLabs', value=f'{l} : [DiscordLabs](https://bots.discordlabs.org/bot/{self.bot.user.id})')
        try:
            await r.send(embed=e1)
        except:
            pass
