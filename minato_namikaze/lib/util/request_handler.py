from __future__ import annotations

import asyncio
import logging
import random
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import aiohttp

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
