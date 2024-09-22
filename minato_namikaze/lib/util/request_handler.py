from __future__ import annotations

import asyncio
import logging
import random
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import aiohttp
import discord
from discord.ext import commands

from .vars import Methods

log = logging.getLogger(__name__)

FATESLIST_BASE_URI = "https://api.fateslist.xyz/"
DISCORD_SERVERVICES_BASE_URI = "https://api.discordservices.net/bot/"


from typing import Literal


async def post_handler(
    method,
    url: str,
    header: dict | None = None,
    headers: dict | None = None,
    data: dict | None = None,
    json: dict | None = None,
    log_data: bool | None = False,
    return_data: bool | None = True,
    return_json: bool | None = False,
    getrequestobj: bool | None = False,
) -> Any:
    if header is None:
        header = {}
    if headers is None:
        headers = {}
    if data is None:
        data = {}
    if json is None:
        json = {}
    header_post = {
        "User-Agent": "Minato Namikaze#6413",
        "X-Ratelimit-Precision": "millisecond",
        "Content-Type": "application/json",
    }
    header_post.update(header)
    header_post.update(headers)
    async with aiohttp.ClientSession() as session, session.request(
        method.name,
        url,
        headers=header_post,
        json=data or json,
    ) as response:
        data = await response.text()  # type: ignore
    if log_data:
        log.info(data)
    if return_data:
        if return_json:
            return data.json()  # type: ignore
        return data
    if getrequestobj:
        return response


async def ratelimit_handler(
    req,
    url: str,
    method: Methods,
    headers: dict,
    data: dict,
    print_logs: bool | None = False,
) -> None:
    if req.status == 408:
        log.info("The site is down thus can't post the commands now")
    if req.status == 429:
        from re import findall

        json_reason = await req.json()
        temp = findall(r"\d+", json_reason.get("reason"))
        res = list(map(int, temp))
        await asyncio.sleep(res[0])
        await post_handler(
            method.name,
            url,
            headers=headers,
            json=data,
            return_data=False,
            log_data=print_logs,
        )
    else:
        await asyncio.sleep(random.randrange(60, 120))


# async def post_commands(
#     bot: commands.AutoShardedBot | commands.Bot | discord.Client,
#     print_logs: bool | None = False,
# ) -> None:
#     # Fateslist
#     # list_to_be_given = []
#     # for cog_name in bot.cogs:
#     #     cog = bot.cogs[cog_name]
#     #     for command in cog.walk_commands():
#     #         if not command.hidden:
#     #             command_dict = {
#     #                 "name": command.name,
#     #                 "description": command.description or command.short_doc,
#     #                 "cmd_type": 0,
#     #                 "vote_locked": False,
#     #                 "premium_only": False,
#     #                 "notes": ["Message Command", "Prefix Required"],
#     #                 "nsfw": False,
#     #                 "examples": [],
#     #                 "doc_link": LinksAndVars.website.value
#     #                 + f"/commands/message_commands/#--{command.name}",
#     #             }
#     #             if command.usage:
#     #                 command_dict.update({"usage": command.usage})
#     #             if command.clean_params or len(command.params) != 0:
#     #                 command_dict.update({"args": list(command.clean_params)})
#     #             if command.full_parent_name is not None:
#     #                 command_dict.update(
#     #                     {"groups": [command.full_parent_name, cog_name]},
#     #                 )
#     #             else:
#     #                 command_dict.update(
#     #                     {"groups": [command.full_parent_name, cog_name]},
#     #                 )
#     #             list_to_be_given.append(command_dict)
#     # # for i in bot.application_commands:
#     # #     app_command_dict = {
#     # #         'name': i.name,
#     # #         'description': i.description,
#     # #         "cmd_type": 1,
#     # #         "vote_locked": False,
#     # #         "premium_only": False,
#     # #         "notes": ['Slash Command'],
#     # #         "nsfw": False,
#     # #         "examples": [],
#     # #         "doc_link": LinksAndVars.website.value+f"/commands/application_commands/#{i.name}",
#     # #         "groups": [],
#     # #         "args": [j.name for j in i.options if i.options],
#     # #         "usage": f'/{i.name}'
#     # #     }
#     # #     list_to_be_given.append(app_command_dict)
#     # final_list = discord.utils.as_chunks(list_to_be_given, 10)
#     # for to_be_post_list in final_list:
#     #     req = await post_handler(
#     #         Methods.POST,
#     #         FATESLIST_BASE_URI + f"bots/{bot.application_id}/commands",
#     #         headers={
#     #             "Authorization": token_get("FATESLIST"),
#     #         },
#     #         json={"commands": to_be_post_list},
#     #         return_data=False,
#     #         getrequestobj=True,
#     #         log_data=print_logs,
#     #     )
#     #     await ratelimit_handler(
#     #         req,
#     #         FATESLIST_BASE_URI + f"bots/{bot.application_id}/commands",
#     #         Methods.POST,
#     #         data={"commands": to_be_post_list},
#     #         headers={
#     #             "Authorization": token_get("FATESLIST"),
#     #         },
#     #         print_logs=print_logs,
#     #     )

#     # # Discord Services
#     # list_to_be_given = []
#     # for cog_name in bot.cogs:
#     #     cog = bot.cogs[cog_name]
#     #     for command in cog.walk_commands():
#     #         if not command.hidden:
#     #             command_dict = {
#     #                 "command": command.name,
#     #                 "desc": command.description or command.short_doc,
#     #             }
#     #             if command.full_parent_name is not None:
#     #                 command_dict.update({"category": str(cog_name)})
#     #             list_to_be_given.append(command_dict)
#     # for i in bot.application_commands:
#     #     app_command_dict = {
#     #         "command": i.name,
#     #         "desc": i.description,
#     #     }
#     #     list_to_be_given.append(app_command_dict)
#     # for i in list_to_be_given:
#     #     req = await post_handler(
#     #         Methods.POST,
#     #         FATESLIST_BASE_URI + f"{bot.application_id}/commands",
#     #         headers={
#     #             "Authorization": token_get("DISCORDSERVICES"),
#     #         },
#     #         json=i,
#     #         return_data=False,
#     #         getrequestobj=True,
#     #         log_data=print_logs,
#     #     )
#     #     await ratelimit_handler(
#     #         req,
#     #         DISCORD_SERVERVICES_BASE_URI + f"{bot.application_id}/commands",
#     #         Methods.POST,
#     #         data=i,
#     #         headers={
#     #             "Authorization": token_get("DISCORDSERVICES"),
#     #         },
#     #         print_logs=print_logs,
#     #     )
#     return
