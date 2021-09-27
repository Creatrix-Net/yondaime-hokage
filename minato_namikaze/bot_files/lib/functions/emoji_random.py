from random import choice


def emoji_random_func(bot):
    guild = bot.get_guild(747480356625711204)
    guild_emojis = choice(guild.emojis)
    if guild_emojis.animated and guild_emojis.is_usable():
        return f'<a:{guild_emojis.name}:{guild_emojis.id}>'
    elif not guild_emojis.animated and guild_emojis.is_usable():
        return f'<:{guild_emojis.name}:{guild_emojis.id}>'
    else:
        emoji_random(bot)
