import configparser
import enum
import gzip
import io
import json
import os
import re
import zipfile
from pathlib import Path
from typing import Any, List, Optional

from sqlalchemy.orm import declarative_base

from .utility import _MissingSentinel

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # In minato_namikaze/ folder
CONFIG_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".ini"
DEFAULT_COMMAND_SELECT_LENGTH = 25
Base = declarative_base()
INVITE_URL_RE = re.compile(
    r"(discord\.(?:gg|io|me|li)|discord(?:app)?\.com\/invite)\/(\S+)", re.I
)

MISSING: Any = _MissingSentinel()

def token_get(tokenname: str = MISSING, all: bool = False) -> Any:
    """Helper function to get the credentials from the environment variables or from the configuration file

    :param tokenname: The token name to access
    :type tokenname: str
    :param all: Return all values from config filename, defaults to False
    :type all: bool, optional
    :raises RuntimeError: When all set :bool:`True` and `.ini` file is not found
    :return: The environment variables data requested if not found then None is returned
    :rtype: Any
    """
    if not all:
        if os.path.isfile(CONFIG_FILE):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            sections = config._sections
            for i in sections:
                for j in i:
                    if j.lower() == tokenname:
                        return config[i][j]
            return
        return os.environ.get(tokenname, "False").strip("\n")
    if os.path.isfile(CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config._sections
    raise RuntimeError("Could not find .ini file")


class envConfig:
    """A class which contains all token configuration"""

    def __init__(self):
        self.data: dict = token_get(all=True)
        for i in self.data:
            for j in self.data.get(i, MISSING):
                setattr(self, j.lower(), self.data[i].get(j))
                setattr(self, j.upper(), self.data[i].get(j))


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
    badges_channel = 920536143458598930
    backup_channel = 922544732918415390
    error_logs_channel = 920190310942908513

    server_id = 920190307595874304
    server_id2 = 920536143244709889

    restartlog_channel1 = 920190310942908508
    restartlog_channel2 = 920536143458598926

    serverlog_channel1 = 920190310942908509
    serverlog_channel2 = 920536143458598927


class Tokens(enum.Enum):
    statcord = token_get("STATCORD")
    dagpi = token_get("DAGPI")
    sentry_link = token_get("SENTRY")

    tenor = token_get("TENOR")
    giphy = token_get("GIPHY")

    token = token_get("TOKEN")
    weather = token_get("WEATHER")


class LinksAndVars(enum.Enum):
    website = "https://minato-namikaze.readthedocs.io/en/latest"

    github = "https://github.com/The-4th-Hokage/yondaime-hokage"
    github_branch = "master"

    bad_links = "https://raw.githubusercontent.com/The-4th-Hokage/bad-domains-list/master/bad-domains.txt"
    listing = (
        "https://raw.githubusercontent.com/The-4th-Hokage/listing/master/listing.json"
    )
    character_data = "https://raw.githubusercontent.com/The-4th-Hokage/naruto-card-game-images/master/img_data.json"

    statuspage_link = "https://minatonamikaze.statuspage.io"
    mal_logo = (
        "https://cdn.myanimelist.net/images/event/15th_anniversary/top_page/item7.png"
    )
    giveaway_image = "https://i.imgur.com/efLKnlh.png"

    version = token_get("VERSION")
    invite_code = "vfXHwS3nmQ"
    timeout = 3.0
    delete_message = 5.0
    owner_ids = [887549958931247137, 837223478934896670, 747729781369602049]

    with gzip.open(
        os.path.join(Path(__file__).resolve().parent.parent, "data", "insult.txt.gz"),
        "rt",
        encoding="utf-8",
    ) as f:
        insults: List[str] = list(
            map(
                lambda a: a.strip(" ").strip("\n").strip("'").strip('"').strip("\\"),
                f.read().split(","),
            )
        )


class RaidMode(enum.Enum):
    off = 0
    on = 1
    strict = 2


class Webhooks(enum.Enum):
    logs = token_get("LOGS")
    feedback = token_get("FEEDBACK")


class Database(enum.Enum):
    database_category_name = "DATABASE"
    database_channel_name = "setup vars"
    antiraid_channel_name = "antiraid"
    mentionspam_channel_name = "mentionspam"
    reaction_roles_channel_name = "reaction roles"
    giveaway_time_channel_name = "giveaway"
    user_blacklist_channel_name = "user blacklist"
    server_blacklist_channel_name = "server blacklist"


@enum.unique
class Methods(enum.IntEnum):
    GET = 1
    POST = 2
    DELETE = 3


with gzip.open(
    os.path.join(
        Path(__file__).resolve().parent.parent,
        "data",
        "periodic_table_data",
        "LATTICES.json.gz",
    ),
    "rt",
    encoding="utf-8",
) as f:
    LATTICES: dict = json.load(f)

with gzip.open(
    os.path.join(
        Path(__file__).resolve().parent.parent,
        "data",
        "periodic_table_data",
        "IMAGES.json.gz",
    ),
    "rt",
    encoding="utf-8",
) as f:
    IMAGES: dict = json.load(f)

with gzip.open(
    os.path.join(
        Path(__file__).resolve().parent.parent,
        "data",
        "periodic_table_data",
        "UNITS.json.gz",
    ),
    "rt",
    encoding="utf-8",
) as f:
    UNITS: dict = json.load(f)

minato_gif = []
with zipfile.ZipFile(BASE_DIR / os.path.join("lib", "data", "minato.zip")) as myzip:
    for i in myzip.namelist():
        with myzip.open(i) as f:
            minato_gif.append((i, io.BytesIO(f.read())))

with zipfile.ZipFile(BASE_DIR / os.path.join("lib", "data", "among_us.zip")) as myzip:
    with myzip.open("amongus.png") as f:
        among_us = io.BytesIO(f.read())
    with myzip.open("amoungus_friends.png") as f:
        among_us_friends = io.BytesIO(f.read())


with gzip.open(
    BASE_DIR
    / os.path.join(
        "lib",
        "data",
        "url_regex.txt.gz",
    ),
    "rt",
    encoding="utf-8",
) as f:
    url_regex = f.read()
