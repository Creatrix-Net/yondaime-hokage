import asyncio
import gzip
import random
from os.path import join
from pathlib import Path

import aiohttp
import requests

from ..classes.embed import Embed
from .vars import *


class PostStats:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def imagelist(self):
        with gzip.open(
                join(
                    Path(__file__).resolve().parent.parent,
                    "data",
                    "vocaloid_images.txt.gz",
                ),
                "rt",
                encoding="utf-8",
        ) as f:
            images_list: list = f.readlines()
        return images_list

    async def delete_commands(self):
        try:
            allcmd = requests.get(
                f"https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/commands",
                headers={
                    "Authorization": BotList.fateslist.value,
                    "Content-Type": "application/json",
                },
            )
            if allcmd.status_code != 404:
                for i in allcmd:
                    for j in allcmd.get(i):
                        requests.delete(
                            f'https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/commands/{j.get("id")}',
                            headers={
                                "Authorization": BotList.fateslist.value,
                                "Content-Type": "application/json",
                            },
                        )
                        await asyncio.sleep(5)
                return True
            return False
        except:
            return False

    async def post_commands(self):
        commands_list = []
        for i in self.bot.commands:
            tuple_notes = (str(i.description)
                           if i.description != "" else str(i.short_doc))
            parameters = [f"<{j}>" for j in i.clean_params]
            dict_append = {
                "cmd_name":
                i.value,
                "vote_locked":
                bool("vote locked" in tuple_notes
                     or "votes lock" in tuple_notes
                     or "vote lock" in tuple_notes),
                "description":
                str(i.description)
                if i.description != "" else str(i.short_doc),
                "cmd_groups":
                i.parents + [i.cog_name] if i.cog_name else i.parents,
                "cmd_type":
                0,
            }
            if i.usage:
                dict_append.update({"examples": [f"){i.value} " + i.usage]})
            if len(parameters) > 0:
                dict_append.update({"args": parameters})
            commands_list.append(dict_append)
        for i in commands_list:
            j = await self.post(
                "https://fateslist.xyz/api/v2/bots/779559821162315787/commands",
                headers={
                    "Authorization": BotList.fateslist.value,
                    "Content-Type": "application/json",
                },
                json=i,
                getrequestobj=True,
            )
            if isinstance(j, int):
                print(j, "The site is down thus can't post the commands now")
                break
            if j.status == 429:
                from re import findall

                json_reason = await j.json()
                temp = findall(r"\d+", json_reason.get("reason"))
                res = list(map(int, temp))
                await asyncio.sleep(res[0])
                k = await self.post(
                    "https://fateslist.xyz/api/v2/bots/779559821162315787/commands",
                    headers={
                        "Authorization": BotList.fateslist.value,
                        "Content-Type": "application/json",
                    },
                    json=i,
                )
            else:
                await asyncio.sleep(5)
        try:
            allcmd = requests.get(
                f"https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/commands",
                headers={
                    "Authorization": BotList.fateslist.value,
                    "Content-Type": "application/json",
                },
            )
            if allcmd.status_code != 404:
                allcmd1 = allcmd.json()
                all_cogs = list(self.bot.cogs.keys())
                for i in allcmd1:
                    for j in allcmd1.get(i):
                        if j.get("cmd_name") in all_cogs:
                            requests.delete(
                                f'https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/commands/{j.get("id")}',
                                headers={
                                    "Authorization": BotList.fateslist.value,
                                    "Content-Type": "application/json",
                                },
                            )
                            await asyncio.sleep(5)
        except:
            pass

    @staticmethod
    async def post(url,
                   headers,
                   data: dict = None,
                   json: dict = None,
                   getrequestobj=False):
        try:
            session = aiohttp.ClientSession()
            request_made = await session.post(url,
                                              headers=headers,
                                              json=data or json)
            await session.close()
            if getrequestobj:
                return request_made
            return request_made.status
        except:
            return 503

    async def post_guild_stats_all(self):
        guildsno = len(self.bot.guilds)
        members = len(set(self.bot.get_all_members()))

        imageslist = self.imagelist
        shards = 1

        a = await self.post(
            f"https://top.gg/api/bots/{self.bot.user.id}/stats",
            headers={"Authorization": BotList.topken.value},
            data={
                "server_count": guildsno,
                "shard_count": shards
            },
        )
        b = await self.post(
            f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats",
            headers={"Authorization": BotList.dblst.value},
            data={
                "guilds": guildsno,
                "users": members
            },
        )
        c = await self.post(
            f"https://discords.com/bots/api/bot/{self.bot.user.id}",
            headers={
                "Authorization": BotList.bfd.value,
                "Content-Type": "application/json",
            },
            json={"server_count": guildsno},
        )
        d = await self.post(
            f"https://api.discordlist.space/v2/bots/{self.bot.user.id}",
            headers={
                "Authorization": f"Bot {BotList.botlist.value}",
                "Content-Type": "application/json",
            },
            json={
                "serverCount": guildsno,
                "active": True
            },
        )
        e = await self.post(
            f"https://discord.boats/api/bot/{self.bot.user.id}",
            headers={"Authorization": BotList.discordboats.value},
            data={"server_count": guildsno},
        )
        f = await self.post(
            f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",
            headers={
                "Authorization": BotList.discordbotsgg.value,
                "Content-Type": "application/json",
            },
            json={
                "guildCount": guildsno,
                "shardCount": shards
            },
        )

        i = await self.post(
            f"https://api.voidbots.net/bot/stats/{self.bot.user.id}",
            headers={
                "Authorization": BotList.voidbot.value,
                "Content-Type": "application/json",
            },
            json={
                "server_count": guildsno,
                "shard_count": shards
            },
        )
        j = await self.post(
            f"https://fateslist.xyz/api/v2/bots/{self.bot.user.id}/stats",
            headers={
                "Authorization": BotList.fateslist.value,
                "Content-Type": "application/json",
            },
            json={
                "guild_count": guildsno,
                "user_count": members,
                "shard_count": shards,
            },
        )
        k = await self.post(
            f"https://api.bladelist.gg/bots/{self.bot.user.id}",
            headers={
                "Authorization": f"Token  {BotList.bladebot.value}",
                "Content-Type": "application/json",
            },
            json={
                "server_count": guildsno,
                "shard_count": shards
            },
        )
        l = await self.post(
            f"https://bots.discordlabs.org/v2/bot/{self.bot.user.id}/stats",
            headers={
                "Authorization": BotList.discordlabs.value,
                "Content-Type": "application/json",
            },
            json={
                "server_count": guildsno,
                "shard_count": shards
            },
        )
        m = await self.post(
            f"https://api.infinitybotlist.com/bot/{self.bot.user.id}",
            headers={"Authorization": BotList.infinity.value},
            json={
                "servers": guildsno,
                "botid": self.bot.user.id,
                "shards": shards
            },
        )

        r = self.bot.get_channel(
            822472454030229545 if not self.bot.local else 870561578347540490)
        e1 = Embed(
            title="Status posted successfully",
            description="[Widgets Link](https://minato-namikaze.readthedocs.io/en/latest/#widgets) [Invite Stats](https://minatonamikaze-invites.herokuapp.com/)",
        )
        e1.set_image(url=random.choice(imageslist).strip("\n"))
        e1.set_thumbnail(url=self.bot.user.avatar.url)

        e1.add_field(
            name="TopGG",
            value=f"{a} : [TopGG](https://top.gg/bot/{self.bot.user.id})")
        e1.add_field(
            name="DiscordBotList",
            value=f"{b} : [DiscordBotList](https://discord.ly/hatsune-miku)",
        )
        e1.add_field(
            name="BotsForDiscord",
            value=f"{c} : [BotsForDiscord](https://botsfordiscord.com/bot/{self.bot.user.id})",
        )
        e1.add_field(
            name="DiscordListSpace",
            value=f"{d} : [DiscordListSpace](https://discordlist.space/bot/{self.bot.user.id})",
        )
        e1.add_field(
            name="DiscordBoats",
            value=f"{e} : [DiscordBoats](https://discord.boats/bot/{self.bot.user.id})",
        )
        e1.add_field(
            name="DiscordBots",
            value=f"{f} : [DiscordBots](https://discord.bots.gg/bots/{self.bot.user.id}/)",
        )
        e1.add_field(
            name="Void Bots",
            value=f"{i} : [Void Bots](https://voidbots.net/bot/{self.bot.user.id}/)",
        )
        e1.add_field(
            name="Fates List",
            value=f"{j} : [Fates List](https://fateslist.xyz/minato/)",
        )
        e1.add_field(
            name="BladeBotList",
            value=f"{k} : [BladeBotList](https://bladelist.gg/bots/{self.bot.user.id}/)",
        )
        e1.add_field(
            name="DiscordLabs",
            value=f"{l} : [DiscordLabs](https://bots.discordlabs.org/bot/{self.bot.user.id})",
        )
        e1.add_field(
            name="Infinity Botlist",
            value=f"{m} : [Infinity Botlist](https://botlist.site/bots/{self.bot.user.id})",
        )
        try:
            await r.send(embed=e1)
        except:
            pass
