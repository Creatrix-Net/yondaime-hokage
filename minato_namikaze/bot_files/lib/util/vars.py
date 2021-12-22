import enum
import os
import re
from pathlib import Path
from secrets import token_urlsafe
from typing import List, Union

import dotenv

dotenv_file = Path(__file__).resolve(
).parent.parent.parent.parent.parent / ".env"


def token_get(tokenname):
    if os.path.isfile(dotenv_file):
        dotenv.load_dotenv(dotenv_file)
    return os.environ.get(tokenname, "False").strip("\n")


BASE_DIR = (
    Path(__file__).resolve().parent.parent.parent
)  # In minato_namikaze/bot_files folder
api_image_store_dir = BASE_DIR / 'images_api_store'

DEFAULT_COMMAND_SELECT_LENGTH = 25


class BotList(enum.Enum):
    dblst = token_get("DISCORDBOTLIST")
    discordbotsgg = token_get("DISCORDBOTSGG")
    topken = token_get("TOPGG")
    bfd = token_get("BOTSFORDISCORD")
    botlist = token_get("BOTLISTSPACE")  # discordlistspace
    discordboats = token_get("DISCORDBOATS")
    voidbot = token_get("VOIDBOT")
    fateslist = token_get("FATESLIST")
    bladebot = token_get("BLADEBOT")
    discordlabs = token_get("DISCORDLABS")
    infinity = token_get("INFINITY")


class ShinobiMatch(list, enum.Enum):
    character_side_exclude = [
        "anbu",
        "iwagakure",
        "kumogakure",
        "kirigakure",
        "otogakure",
        "sunagakure",
        "akatsuki",
        "konohagakure",
    ]

    name_exclusion = character_side_exclude + [
        "naruto",
        "sasuke" "jiraya",
        "namikaze",
        "sarutobi",
        "yamanaka",
        "akimichi",
        "aburame",
        "uzumaki",
        "hyuga",
        "otsutsuki",
        "nara",
        "senju",
        "uchiha",
        "kakashi",
        "sakura",
    ]


@enum.unique
class ChannelAndMessageId(enum.IntEnum):
    shinobi_character_channel = 922037658589466675

    welcome_channel = 920190310657699892  # This is only for the support server
    roles_channel = 920190310657699893  # This is  for the private server

    badges_channel = 920536143458598930
    backup_channel = 922544732918415390
    error_logs_channel = 920190310942908513
    traceback_channel = 922752004525260810

    server_id = 920190307595874304
    server_id2 = 920536143244709889

    tags = 920536143458598931

    restartlog_channel1 = 920190310942908508
    restartlog_channel2 = 920536143458598926


class Tokens(enum.Enum):
    statcord = token_get("STATCORD")
    dagpi = token_get("DAGPI")
    chatbot = token_get("CHATBOTTOKEN")
    sentry_link = token_get("SENTRY")
    token = token_get("TOKEN")


class LinksAndVars(enum.Enum):
    website = token_get("WEBSITE")

    github = token_get("GITHUB")
    github_branch = "master"

    version = token_get("VERSION")
    timeout = 3.0

    with open(
        os.path.join(Path(__file__).resolve().parent.parent,
                     "text", "insult.txt")
    ) as f:
        insults: List[str] = list(
            map(
                lambda a: a.strip(" ").strip("\n").strip(
                    "'").strip('"').strip("\\"),
                f.read().split(","),
            )
        )


@enum.unique
class SetupVars(str, enum.Enum):
    warns = "Warning of the server members will be logged here."
    support = "This channel will be used as a support channel for this server."
    ban = "This channel will be used to log the server bans."
    unban = "Unbans of the server will be logged here."
    feedback = "This channel will be used to log the feedbacks given by members."


class RaidMode(enum.Enum):
    off = 0
    on = 1
    strict = 2

    def __str__(self):
        return self.name
