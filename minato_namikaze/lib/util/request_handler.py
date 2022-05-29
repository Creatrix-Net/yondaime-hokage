import asyncio
import logging, random
from typing import Dict, Optional, Union, Any
import aiohttp
import discord
import sentry_sdk
from discord.ext import commands
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.modules import ModulesIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

from .vars import Methods, Tokens, token_get, LinksAndVars

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)

sentry_sdk.init(
    Tokens.sentry_link.value,
    traces_sample_rate=1.0,
    integrations=[
        AioHttpIntegration(),
        ThreadingIntegration(),
        LoggingIntegration(),
        ModulesIntegration(),
    ],
)

FATESLIST_BASE_URI = 'https://api.fateslist.xyz/'
DISCORD_SERVERVICES_BASE_URI = 'https://api.discordservices.net/bot/'

async def post_handler(
    method: Methods,
    url: str,
    header: Optional[Dict] = None, 
    headers: Optional[Dict] = None,
    data: Optional[Dict] = None, 
    json: Optional[Dict] = None,
    log_data: Optional[bool] = False, 
    return_data: Optional[bool] = True, 
    return_json: Optional[bool] = False,
    getrequestobj: Optional[bool] = False
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
        'Content-Type' : 'application/json'
    }
    header_post.update(header)
    header_post.update(headers)
    async with aiohttp.ClientSession() as session:
        async with session.request(method.name, url, headers=header_post, json=data or json) as response:
            data = await response.text()
    if log_data:
        log.info(data)
    if return_data:
        if return_json:
            return data.json()
        return data
    if getrequestobj:
        return response


async def ratelimit_handler(
    req,
    url: str,  
    method: Methods,
    headers: Dict,
    data: Dict, 
    print_logs: Optional[bool] = False
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
            log_data=print_logs
        )
    else:
        await asyncio.sleep(random.randrange(60,120))


async def post_commands(
    bot: Union[
        commands.AutoShardedBot,
        commands.Bot, 
        discord.Client
    ], 
    print_logs: Optional[bool] = False
) -> None:
    #Fateslist
    list_to_be_given = []
    for cog_name in bot.cogs:
        cog = bot.cogs[cog_name]
        for command in cog.walk_commands():
            if not command.hidden:
                command_dict = {
                    "name": command.name,
                    "description": command.description or command.short_doc,
                    "cmd_type": 0,
                    "vote_locked": False,
                    "premium_only": False,
                    "notes": ['Message Command', 'Prefix Required'],
                    "nsfw": False,
                    "examples": [],
                    "doc_link": LinksAndVars.website.value+f"/commands/message_commands/#--{command.name}"
                }
                if command.usage:
                    command_dict.update({"usage": command.usage})
                if command.clean_params or len(command.params) != 0:
                    command_dict.update({"args": list(command.clean_params)})
                if command.full_parent_name is not None:
                    command_dict.update({"groups": [command.full_parent_name,cog_name]})
                else:
                    command_dict.update({"groups": [command.full_parent_name,cog_name]})
                list_to_be_given.append(command_dict)
    # for i in bot.application_commands:
    #     app_command_dict = {
    #         'name': i.name,
    #         'description': i.description,
    #         "cmd_type": 1,
    #         "vote_locked": False,
    #         "premium_only": False,
    #         "notes": ['Slash Command'],
    #         "nsfw": False,
    #         "examples": [],
    #         "doc_link": LinksAndVars.website.value+f"/commands/application_commands/#{i.name}",
    #         "groups": [],
    #         "args": [j.name for j in i.options if i.options],
    #         "usage": f'/{i.name}'
    #     }
    #     list_to_be_given.append(app_command_dict)
    final_list = discord.utils.as_chunks(list_to_be_given, 10)
    for to_be_post_list in final_list:
        req = await post_handler(
            Methods.POST,
            FATESLIST_BASE_URI + f"bots/{bot.application_id}/commands",
            headers={
                "Authorization": token_get('FATESLIST'),
            },
            json={"commands": to_be_post_list},
            return_data=False,
            getrequestobj=True,
            log_data=print_logs
        )
        await ratelimit_handler(
            req,
            FATESLIST_BASE_URI + f"bots/{bot.application_id}/commands",
            Methods.POST,
            data={"commands": to_be_post_list},
            headers={
                "Authorization": token_get('FATESLIST'),
            },
            print_logs=print_logs
        )

    #Discord Services
    list_to_be_given = []
    for cog_name in bot.cogs:
        cog = bot.cogs[cog_name]
        for command in cog.walk_commands():
            if not command.hidden:
                command_dict = {
                    "command": command.name,
                    "desc": command.description or command.short_doc,
                }
                if command.full_parent_name is not None:
                    command_dict.update({"category": str(cog_name)})
                list_to_be_given.append(command_dict)
    for i in bot.application_commands:
        app_command_dict = {
            'command': i.name,
            'desc': i.description,
        }
        list_to_be_given.append(app_command_dict)
    for i in list_to_be_given:
        req = await post_handler(
            Methods.POST,
            FATESLIST_BASE_URI + f"{bot.application_id}/commands",
            headers={
                "Authorization": token_get('DISCORDSERVICES'),
            },
            json=i,
            return_data=False,
            getrequestobj=True,
            log_data=print_logs
        )
        await ratelimit_handler(
            req,
            DISCORD_SERVERVICES_BASE_URI + f"{bot.application_id}/commands",
            Methods.POST,
            data=i,
            headers={
                "Authorization": token_get('DISCORDSERVICES'),
            },
            print_logs=print_logs
        )
