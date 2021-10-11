import random

import discord

from .vars import ChannelAndMessageId


def convert(time):
    pos = ["s", "m", "h", "d"]
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 24*3600}
    unit = time[-1]
    if unit not in pos:
        return -1
    try:
        timeVal = int(time[:-1])
    except:
        return -2

    return timeVal*time_dict[unit]


#shinobi match!

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
    
def return_random_5characters(characters: dict) -> dict:
    keys = list(characters.keys())  # List of keys
    random.shuffle(keys)
    return [
        random.choice(keys),
        random.choice(keys),
        random.choice(keys),
        random.choice(keys),
        random.choice(keys)
    ]

def format_character_name(character_name: str) -> str:
    if character_name.split('(')[-1].strip(' ').strip(')').lower() in ChannelAndMessageId.character_side_exclude.name:
        return character_name.split('(')[0].strip(' ').title()
    return character_name.strip(' ').title()


def return_matching_emoji(ctx,name):
    def emoji_predicate(emoji, name):
        return emoji.name.lower() in name
    if name.split('(')[-1].strip(' ').strip(')').lower() in ChannelAndMessageId.character_side_exclude.name:
        name = name.split('(')[-1].strip(' ').strip(')').lower()
        for i in ctx.bot.get_guild(ChannelAndMessageId.testing_server_id.name).emojis:
            if emoji_predicate(i, name):
                return i
    else:
        name = name.lower().strip(' ').lower()
        for i in ctx.bot.get_guild(ChannelAndMessageId.testing_server_id.name).emojis:
            if emoji_predicate(i, name):
                return i