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
    spacebot = token_get("SPACEBOT")
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
    shinobi_character_channel = 869433768593719327
    welcome_channel = 747660913116577903  # This is only for the support server
    roles_channel = 777189846862266408

    error_logs_channel = 830366314761420821

    server_id = 747480356625711204
    testing_server_id = 869085099470225508

    help_smile_emoji = 848961696047300649


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
