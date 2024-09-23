from __future__ import annotations

import os
import re
from collections.abc import Iterator
from collections.abc import MutableSequence
from typing import Any
from typing import Generic
from typing import List
from typing import TypeVar
from urllib.parse import urlparse
from urllib.parse import uses_netloc

import aiohttp
import discord

from .vars import BASE_DIR
from .vars import ChannelAndMessageId
from .vars import LinksAndVars
from .vars import url_regex

INVITE_URL_RE = re.compile(
    r"(discord\.(?:gg|io|me|li)|discord(?:app)?\.com\/invite)\/(\S+)",
    re.I,
)
IMAGE_LINKS = re.compile(
    r"(https?:\/\/[^\"\'\s]*\.(?:png|jpg|jpeg|gif|png|svg)(\?size=[0-9]*)?)"
)
EMOJI_REGEX = re.compile(r"(<(a)?:[a-zA-Z0-9\_]+:([0-9]+)>)")
MENTION_REGEX = re.compile(r"<@!?([0-9]+)>")
ID_REGEX = re.compile(r"[0-9]{17,}")

_T = TypeVar("_T")


class UniqueList(MutableSequence, Generic[_T]):
    __slots__ = "_list"

    def __init__(self) -> None:
        self._list = []

    def __bool__(self) -> bool:
        return bool(self._list)

    def __eq__(self, other) -> bool:
        return self._list == other

    def __len__(self) -> int:
        return len(self._list)

    def __iter__(self) -> Iterator:
        return iter(self._list)

    def __length_hint__(self) -> int:
        return self.__len__()

    def __reversed__(self) -> Iterator:
        return reversed(self._list)

    def __missing__(self, index: int) -> _T:
        return self._list[index]

    def __delitem__(self, index: int) -> None:
        del self._list[index]

    def __getitem__(self, index: int) -> _T:
        return self._list[index]

    def __setitem__(self, index: int, value: _T) -> None:
        self._list[index] = value

    def __contains__(self, value: _T) -> bool:
        return value in self._list

    def __repr__(self) -> str:
        return repr(self._list)

    def unique_add(self, value: _T) -> None:
        if value not in self._list:
            self._list.append(value)

    def append(self, value: _T) -> None:
        self.unique_add(value)

    def extend(self, value: Iterator) -> None:
        for i in value:
            self.unique_add(i)

    def remove(self, value: _T) -> None:
        self._list.remove(value)

    def pop(self, index: int = -1) -> _T:
        return self._list.pop(index)

    def clear(self) -> None:
        self._list.clear()

    def index(self, value: _T) -> int:
        return self._list.index(value)

    def count(self, value: _T) -> int:
        return self._list.count(value)

    def reverse(self) -> None:
        self._list.reverse()

    def sort(self, *args: Any, **kwargs: Any) -> None:
        self._list.sort(*args, **kwargs)

    def copy(self):
        return self._list.copy()

    def insert(self, index: int, value: _T) -> None:
        self._list.insert(index, value)


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other):
        return False

    def __bool__(self):
        return False

    def __hash__(self):
        return 0

    def __repr__(self):
        return "..."

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0


MISSING: Any = _MissingSentinel()


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
    if (
        character_name.split("(")[-1].strip(" ").strip(")").lower()
        in ChannelAndMessageId.character_side_exclude.name
    ):
        return character_name.split("(")[0].strip(" ").title()
    return character_name.strip(" ").title()


async def return_matching_emoji(bot, name) -> discord.Emoji:
    return discord.utils.get(
        (await bot.fetch_guild(ChannelAndMessageId.server_id.value)).emojis,
        name=name.lower(),
    ) or discord.utils.get(
        (await bot.fetch_guild(ChannelAndMessageId.server_id2.value)).emojis,
        name=name.lower(),
    )


async def detect_bad_domains(message_content: str) -> list:
    try:
        url1 = [x[0] for x in re.findall(url_regex, message_content)]
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url2 = [x[0] for x in re.findall(regex, message_content)]
        url = url1 + url2
        for i in message_content.split():
            url.append(i.lower())
        if len(url) == 0:
            return []

        async with aiohttp.ClientSession() as session, session.get(
            LinksAndVars.bad_links.value,
        ) as resp:
            list_of_bad_domains = (await resp.text()).split("\n")

        detected_urls = []
        for i in url:
            if len(i.split("//")) != 0:
                try:
                    parsed_url = urlparse(
                        (
                            i.lower().strip("/")
                            if i.split("://")[0].lower() in uses_netloc
                            else f'//{i.strip("/")}'
                        ),
                    )
                    if parsed_url.hostname in list_of_bad_domains:
                        detected_urls.append(parsed_url.hostname)
                except:
                    pass
    except IndexError:
        return []
    return detected_urls


def return_all_cogs() -> list[str]:
    """A Helper function to return all the cogs except the jishkaku

    :return: List of all cogs present as a file
    :rtype: List[str]
    """
    list_to_be_given: list = []
    cog_dir = BASE_DIR / "cogs"
    for filename in list(set(os.listdir(cog_dir))):
        if os.path.isdir(cog_dir / filename):
            for i in os.listdir(cog_dir / filename):
                if (
                    i.endswith(".py")
                    and not i.startswith("__init__")
                    and not i.endswith(".pyc")
                ):
                    list_to_be_given.append(f'{filename.strip(" ")}.{i[:-3]}')
        else:
            if (
                filename.endswith(".py")
                and not filename.startswith("__init__")
                and not filename.endswith(".pyc")
            ):
                list_to_be_given.append(filename[:-3])

    return list_to_be_given
