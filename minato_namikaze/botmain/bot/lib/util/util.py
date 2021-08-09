import random, discord
from .vars import uchiha2_emoji,uchiha1_emoji,senju2_emoji,senju1_emoji,server_id

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

def return_uchiha_emoji(ctx):
    return discord.utils.get(
        ctx.bot.get_guild(server_id).emojis, 
        id=random.choice([uchiha1_emoji,uchiha2_emoji])
        )

def return_senju_emoji(ctx):
    return discord.utils.get(
        ctx.bot.get_guild(server_id).emojis, 
        id=random.choice([senju1_emoji,senju2_emoji]
            )
        )