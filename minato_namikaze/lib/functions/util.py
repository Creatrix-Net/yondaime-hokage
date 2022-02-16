import aiohttp
import re
import discord
from ..util.vars import ChannelAndMessageId, LinksAndVars, url_regex
from urllib.parse import urlparse,uses_netloc

INVITE_URL_RE = re.compile(r"(discord\.(?:gg|io|me|li)|discord(?:app)?\.com\/invite)\/(\S+)", re.I)


def filter_invites(to_filter: str) -> str:
    """Get a string with discord invites sanitized.

    Will match any discord.gg, discordapp.com/invite, discord.com/invite, discord.me, or discord.io/discord.li
    invite URL.

    Parameters
    ----------
    to_filter : str
        The string to filter.

    Returns
    -------
    str
        The sanitized string.

    """
    return INVITE_URL_RE.sub("[SANITIZED INVITE]", to_filter)


def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 24 * 3600}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except:
        return -2

    return timeVal * time_dict[unit]


def humanize_attachments(attachments: list) -> list:
    attachment_list = []
    if len(attachments) == 0:
        return []
    for i in attachments:
        try:
            attachment_list.append(i.url)
        except:
            attachment_list.append(i)
    return []


def format_character_name(character_name: str) -> str:
    if (character_name.split("(")[-1].strip(" ").strip(")").lower()
            in ChannelAndMessageId.character_side_exclude.name):
        return character_name.split("(")[0].strip(" ").title()
    return character_name.strip(" ").title()


async def return_matching_emoji(bot, name) -> discord.Emoji:
    return discord.utils.get((await bot.fetch_guild(ChannelAndMessageId.server_id.value)).emojis, name=name.lower()) or discord.utils.get((await bot.fetch_guild(ChannelAndMessageId.server_id2.value)).emojis, name=name.lower())


async def detect_bad_domains(message_content: str) -> list:
    url1 = [x[0] for x in re.findall(url_regex,message_content)]
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url2 = [x[0] for x in re.findall(regex,message_content)] 
    url = url1 + url2
    for i in message_content.split():
        url.append(i.lower())
    if len(url) == 0:
        return []
        
    async with aiohttp.ClientSession() as session:
        async with session.get(LinksAndVars.bad_links.value) as resp:
            list_of_bad_domains = (await resp.text()).split('\n')
        
    detected_urls = []
    for i in url:
        if len(i.split('//')) != 0:
            try:
                parsed_url = urlparse(i.lower().strip('/') if i.split('://')[0].lower() in uses_netloc else f'//{i.strip("/")}')
                if parsed_url.hostname in list_of_bad_domains:
                    detected_urls.append(parsed_url.hostname)
            except:
                pass
    return detected_urls