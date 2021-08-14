import requests

from ..classes import ErrorEmbed
from ..util.vars import *


def votedVoidBots(ctx):
    e1 = requests.get(f'http://api.voidbots.net/bot/voted/{ctx.bot.user.id}/{ctx.message.author.id}',
                      headers={"Authorization": voidbot}
                      )
    try:
        e12 = e1.json().get('voted', False)
    except requests.exceptions.ConnectionError:
        e12 = True
    except:
        e12 = False
    return e12


def votedTopgg(ctx):
    a = requests.get(
        f'https://top.gg/api/bots/{ctx.bot.user.id}/check',
        params={'userId': ctx.message.author.id},
        headers={
            "Authorization": topken
        }
    )
    try:
        a_list = True if a.json().get('voted') >= 1 else False
    except requests.exceptions.ConnectionError:
        a_list = True
    except:
        a_list = False
    return a_list


def votedbotsfordiscord(ctx):
    c = requests.get(f'https://botsfordiscord.com/api/bot/{ctx.bot.user.id}/votes',
                     headers={'Authorization': bfd,
                              'Content-Type': 'application/json'},
                     )
    try:
        c_list = True if str(ctx.message.author.id) in c.json().get(
            'hasVoted24', False) else False
    except requests.exceptions.ConnectionError:
        c_list = True
    except:
        c_list = False
    return c_list


def voteddiscordboats(ctx):
    d = requests.get(f'https://discord.boats/api/bot/{ctx.bot.user.id}/voted',
                    params={'id': ctx.message.author.id}
                    )
    try:
        d_list = d.json().get('voted', False)
    except requests.exceptions.ConnectionError:
        d_list = True
    except:
        d_list = False
    return d_list


def votedfateslist(ctx):
    f = requests.get(f'https://fateslist.xyz/api/v2/bots/{ctx.bot.user.id}/votes',
                     headers={"Authorization": fateslist},
                     params={'user_id': ctx.message.author.id}
                     )
    try:
        f1 = f.json().get('voted', False)
    except requests.exceptions.ConnectionError:
        f1 = True
    except:
        f1 = False
    return f1


def votedbladebotlist(ctx):
    g = requests.get(
        f'https://bladebotlist.xyz/api/bots/{ctx.bot.user.id}/votes/{ctx.message.author.id}',
    )
    try:
        g1 = g.json().get('voted', False)
    except requests.exceptions.ConnectionError:
        g1 = True
    except:
        g1 = False
    return g1


def voteddiscordlistspace(ctx):
    h = requests.get(
        f'https://api.discordlist.space/v2/bots/{ctx.bot.user.id}/status/{ctx.message.author.id}',
        headers={"Authorization": botlist}
    )
    try:
        h1 = h.json().get('upvoted', False)
    except requests.exceptions.ConnectionError:
        h1 = True
    except:
        h1 = False
    return h1


def generatevoteembed(ctx, *argv):
    list_dict = {
        'top.gg': 'https://top.gg/images/dblnew.png',
        'discordlist.space': 'https://discordlist.space/img/apple-touch-icon.png',
        'botsfordiscord': 'https://botsfordiscord.com/img/favicons/apple-touch-icon-57x57.png',
        'discord.boats': 'https://discord.boats/apple-icon-57x57.png',
        'fateslist': 'https://fateslist.xyz/static/botlisticon.webp',
        'bladebotlist': 'https://bladebotlist.xyz/img/logo.png',
        'voidbots': 'https://voidbots.net/assets/img/logo.png',
    }
    site_dict = {
        'top.gg': f'https://top.gg/bot/{ctx.bot.user.id}',
        'discordlist.space': f'https://discordlist.space/bot/{ctx.bot.user.id}',
        'botsfordiscord': f'https://botsfordiscord.com/bot/{ctx.bot.user.id}',
        'discord.boats': f'https://discord.boats/bot/{ctx.bot.user.id}',
        'fateslist': f'https://fateslist.xyz/bot/{ctx.bot.user.id}',
        'bladebotlist': f'https://bladebotlist.xyz/bot/{ctx.bot.user.id}',
        'voidbots': f'https://voidbots.net/bot/{ctx.bot.user.id}/',
    }
    if isinstance(argv[0], str):
        e = ErrorEmbed(
            title='Vote Locked!',
            description=f'''You didn\'t vote for me in **[{argv[0].capitalize()}]({site_dict[argv[0].lower()]})** :angry:. The `{ctx.prefix}{ctx.command.name}` is **vote locked**.
            [Click Here]({site_dict[argv[0].lower()]}) to __vote__ for me in **{argv[0].capitalize()}** :wink:.
            ''',
            timestamp=ctx.message.created_at,
        )
        e.set_thumbnail(url=list_dict[argv[0].lower()])
        e.set_author(
            name=ctx.message.author,
            url=site_dict[argv[0].lower()],
            icon_url = ctx.message.author.avatar_url
        )
        e.set_footer(text=f'Vote for us in {argv[0].lower()} and then enjoy the `{ctx.command.name}` command.')
    else:
        join_string = "\n・"
        e = ErrorEmbed(
            title='Vote Locked!',
            description=f'You need to **vote for me** in the **following botlists** :smile: :\n・{join_string.join(list(f"**[{i.capitalize()}]({site_dict[i.lower()]})**" for i in argv[0]))}',
            timestamp=ctx.message.created_at
        )
        e.set_author(
            name=ctx.message.author,
            url=website,
            icon_url = ctx.message.author.avatar_url
        )
        e.set_thumbnail(url=ctx.message.author.avatar_url)
        e.set_footer(text=f'Vote for us in the above mentioned botlists and then enjoy the `{ctx.command.name}` command.')
    return e