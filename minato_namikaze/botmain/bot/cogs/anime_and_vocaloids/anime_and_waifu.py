import time
from typing import Optional

import DiscordUtils
from discord.ext import commands
from mal import Anime, AnimeSearch, Manga, MangaSearch

from ...lib import Embed, votedVoidBots, votedTopgg, votedbotsfordiscord, voteddiscordboats, votedfateslist, votedbladebotlist, voteddiscordlistspace, generatevoteembed


def format_related_anime_manga(dict_related_anime):
    formatted_string = '\n'
    for i in dict_related_anime:
        formatted_string += f'・**{i.capitalize()}**: {" ,".join(dict_related_anime[i])} ;\n'
    return formatted_string


def format_staff(staff):
    staff_string = '\n'
    for k in staff:
        staff_string += f'・**{k.name}**: {k.role}\n'
    return staff_string


def format_characters(character):
    character_string = '\n'
    for k in character:
        character_string += f'・**{k.name}** \n@role: **{k.role}** \nVoice Actor: **{k.voice_actor}**\n\n'
    return character_string


def format_manga_characters(character):
    character_string = '\n'
    for k in character:
        character_string += f'・**{k.name}** \n@role: **{k.role}**\n\n'
    return character_string


class AnimeandManga(commands.Cog, name='Anime and Manga'):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Some anime and manga related commands (vote locked).'

    # search anime
    @commands.command(
        description='Searches Anime from MAL and displays the first 10 search result.',
        usage='<anime.name>',
        aliases=['anisearch', 'animesearchbyname',
                 'anime_search_by_name', 'searchanime', 'searchani']
    )
    async def animesearch(self, ctx, *, anime_name: str):
        '''Searches Anime from MAL and displays the first 10 search result.'''
        if not votedVoidBots(ctx):
            await ctx.send(embed=generatevoteembed(ctx, 'voidbots'))
            return
            
        search = AnimeSearch(str(anime_name).strip(' ').lower())
        search_results = search.results[:10]
        description = ''
        for i, k in enumerate(search_results):
            description += f'{i+1}. **{k.title}**\n'
        e1 = Embed(
            title=f'Anime search results for {str(anime_name).capitalize()}',
            description=description[:4096],
            timestamp=ctx.message.created_at
        )
        e1.set_footer(
            text=f'Showing 10 results out of {len(search.results)} | Use the recations of this message to paginate',
            icon_url='https://cdn.myanimelist.net/images/event/15th_anniversary/top_page/item7.png'
        )
        embeds = [e1]
        for i in search_results:
            e = Embed(
                title=i.title,
                description=i.synopsis,
                timestamp=ctx.message.created_at
            )
            e.add_field(name='**Score**', value=f'{i.score} :star:')
            e.add_field(name='**Anime Type**', value=i.type)
            e.add_field(name='**MAL Url**', value=f'[CLICK HERE]({i.url})')
            e.add_field(name='**MAL ID**', value=i.mal_id)
            e.set_image(url=i.image_url)
            e.set_footer(
                text=f'{i.title} | {i.mal_id} | {i.score} stars', icon_url=i.image_url)
            embeds.append(e)

        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)


    # about anime
    @commands.command(
        description='Displays about the anime using the MAL ANIME ID. get it by using animesearch command.',
        usage='<mal.id>',
        aliases=['aniabout', 'animeabout', 'anime_about_by_mal_id',
                 'knowanime', 'aboutani', 'anime']
    )
    async def aboutanime(self, ctx, mal_id: int):
        '''Displays about the anime using the MAL ANIME ID. get it by using animesearch command.'''
        if not votedTopgg(ctx):
            await ctx.send(embed=generatevoteembed(ctx, 'top.gg'))
            return
        message = await ctx.send(':mag: Searching...', delete_after=5)
        anime = Anime(int(mal_id))
        embeds = []
        e = Embed(
            title=anime.title,
            description=anime.synopsis[:4096],
            timestamp=ctx.message.created_at
        )
        e.add_field(name=':japanese_castle: **Title in Japanese**',
                    value=f'{anime.title_japanese}')
        e.add_field(name='**Title Synonyms**',
                    value=' ,'.join(anime.title_synonyms))
        e.add_field(name=':star: **Score**', value=f'{anime.score} :star:')
        e.add_field(name=':dividers: **Type**', value=anime.type)
        e.add_field(name=':link: **MAL Url**',
                    value=f'[CLICK HERE]({anime.url})')
        e.add_field(name=':id: **MAL ID**', value=anime.mal_id)
        e.add_field(name=':hourglass_flowing_sand: **Status**',
                    value=anime.status)
        e.add_field(name=':arrow_right: **Genre**',
                    value=' ,'.join(anime.genres))
        e.add_field(name=':trophy: **Rank**', value=anime.rank)
        e.add_field(name='**Popularity**', value=f'#{anime.popularity}')
        e.add_field(name=':minidisc: **No. of Episodes**',
                    value=anime.episodes)
        e.add_field(name='**Premire(d)**', value=anime.premiered)
        e.add_field(name=':calendar_spiral: **Air(ed/ing)**',
                    value=anime.aired)
        e.add_field(name='**Broadcast**', value=anime.broadcast)
        e.add_field(name='**Producers**', value=' ,'.join(anime.producers))
        e.add_field(name='**Licensors**', value=' ,'.join(anime.licensors))
        e.add_field(name=':microphone2: **Studios**',
                    value=' ,'.join(anime.studios))
        e.add_field(name=':information_source: **Source**', value=anime.source)
        e.add_field(name=':stopwatch: **Duration**', value=anime.duration)
        e.add_field(name='**Rating**', value=anime.rating)
        if len(format_related_anime_manga(anime.related_anime)) < 1024:
            e.add_field(name='**Related Anime**',
                        value=format_related_anime_manga(anime.related_anime))
        else:
            e1 = Embed(
                title='Related Anime',
                description=format_related_anime_manga(
                    anime.related_anime)[:4096]
            )
            e1.set_footer(
                text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
            embeds.append(e1)
        if len(' ,'.join(anime.opening_themes)) <= 1000:
            e.add_field(name=':play_pause: **Opening Theme(s)**',
                        value='・\n'.join(anime.opening_themes))
        else:
            e1 = Embed(
                title=':play_pause: Opening Theme(s)',
                description='・\n'.join(anime.opening_themes)[:4096]
            )
            e1.set_footer(
                text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
            embeds.append(e1)
        if len(' ,'.join(anime.ending_themes)) <= 1000:
            e.add_field(name=':stop_button: **Ending Theme(s)**',
                        value='・\n'.join(anime.ending_themes))
        else:
            e1 = Embed(
                title=':stop_button: Ending Theme(s)',
                description='・\n'.join(anime.ending_themes)[:4096]
            )
            e1.set_footer(
                text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
            embeds.append(e1)
        if len(format_staff(anime.staff)) <= 700:
            e.add_field(name=':factory_worker: Staff',
                        value=format_staff(anime.staff))
        else:
            e1 = Embed(
                title=':factory_worker: Staff',
                description=format_staff(anime.staff)[:4096]
            )
            e1.set_footer(
                text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
            embeds.append(e1)
        if len(format_characters(anime.characters)) <= 600:
            e.add_field(name='**Characters**',
                        value=format_characters(anime.characters))
        else:
            e1 = Embed(
                title='Characters',
                description=format_characters(anime.characters)[:4096]
            )
            e1.set_footer(
                text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
            embeds.append(e1)
        e.set_image(url=anime.image_url)
        e.set_footer(
            text=f'{anime.title_japanese} | {anime.mal_id} | {anime.score} stars', icon_url=anime.image_url)
        await ctx.send(embed=e)
        for i in embeds:
            await ctx.send(embed=i)
            time.sleep(0.5)


    # search manga
    @commands.command(
        description='Searches Manga from MAL and displays the first 10 search result.',
        usage='<manga.name>',
        aliases=['magsearch', 'mangasearchbyname',
                 'manga_search_by_name', 'searchmanga', 'searchmag']
    )
    async def mangasearch(self, ctx, *, manga_name: str):
        '''Searches Manga from MAL and displays the first 10 search result.'''
        if not votedbotsfordiscord(ctx):
            await ctx.send(embed=generatevoteembed(ctx, 'botsfordiscord'))
            return
        search = MangaSearch(str(manga_name).strip(' ').lower())
        search_results = search.results[:10]
        description = ''
        for i, k in enumerate(search_results):
            description += f'{i+1}. **{k.title}**\n'
        e1 = Embed(
            title=f'Manga search results for {str(manga_name).capitalize()}',
            description=description,
            timestamp=ctx.message.created_at
        )
        e1.set_footer(
            text=f'Showing 10 results out of {len(search.results)} | Use the recations of this message to paginate',
            icon_url='https://cdn.myanimelist.net/images/event/15th_anniversary/top_page/item7.png'
        )
        embeds = [e1]
        for i in search_results:
            e = Embed(
                title=i.title,
                description=i.synopsis,
                timestamp=ctx.message.created_at
            )
            e.add_field(name='**Score**', value=f'{i.score} :star:')
            e.add_field(name='**Manga Type**', value=i.type)
            e.add_field(name='**MAL Url**', value=f'[CLICK HERE]({i.url})')
            e.add_field(name='**MAL ID**', value=i.mal_id)
            e.set_image(url=i.image_url)
            e.set_footer(
                text=f'{i.title} | {i.mal_id} | {i.score} stars', icon_url=i.image_url)
            embeds.append(e)

        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        await paginator.run(embeds)


    # about manga
    @commands.command(
        description='Displays about the manga using the MAL MANGA ID. get it by using mangasearch command.',
        usage='<mal.id>',
        aliases=['magabout', 'mangaabout', 'manga_about_by_mal_id',
                 'knowmanga', 'aboutmag', 'manga']
    )
    async def aboutmanga(self, ctx, mal_id: int):
        '''Displays about the manga using the MAL MANGA ID. get it by using mangasearch command.'''
        if not voteddiscordboats(ctx):
            await ctx.send(embed=generatevoteembed(ctx, 'discord.boats'))
            return
        message = await ctx.send(':mag: Searching...', delete_after=5)
        manga = Manga(int(mal_id))
        embeds = []
        e = Embed(
            title=manga.title,
            description=manga.synopsis[:4096],
            timestamp=ctx.message.created_at
        )
        e.add_field(name=':japanese_castle: **Title in Japanese**',
                    value=f'{manga.title_japanese}')
        e.add_field(name='**Title Synonyms**',
                    value=' ,'.join(manga.title_synonyms))
        e.add_field(name=':star: **Score**', value=f'{manga.score} :star:')
        e.add_field(name=':dividers: **Type**', value=manga.type)
        e.add_field(name=':link: **MAL Url**',
                    value=f'[CLICK HERE]({manga.url})')
        e.add_field(name=':id: **MAL ID**', value=manga.mal_id)
        e.add_field(name=':hourglass_flowing_sand: **Status**',
                    value=manga.status)
        e.add_field(name=':arrow_right: **Genre**',
                    value=' ,'.join(manga.genres))
        e.add_field(name=':trophy: **Rank**', value=manga.rank)
        e.add_field(name='**Popularity**', value=f'#{manga.popularity}')
        e.add_field(name=':book: **No. of Chapters**', value=manga.chapters)
        e.add_field(name=':books: **Volumes**', value=manga.volumes)
        e.add_field(name=':pen_fountain: **Author(s)**',
                    value='\n・'.join(manga.authors))
        e.add_field(name=':map: **Published**', value=manga.published)
        if len(format_manga_characters(manga.characters)) <= 600:
            e.add_field(name='**Characters**',
                        value=format_manga_characters(manga.characters))
        else:
            e1 = Embed(
                title='Characters',
                description=format_manga_characters(manga.characters)[:4096]
            )
            e1.set_footer(
                text=f'{manga.title_japanese} | {manga.mal_id} | {manga.score} stars', icon_url=manga.image_url)
            embeds.append(e1)
        if len(format_related_anime_manga(manga.related_manga)) < 1024:
            e.add_field(name='**Related Manga**',
                        value=format_related_anime_manga(manga.related_manga))
        else:
            e1 = Embed(
                title='Related Manga',
                description=format_related_anime_manga(
                    manga.related_manga)[:4096]
            )
            e1.set_footer(
                text=f'{manga.title_japanese} | {manga.mal_id} | {manga.score} stars', icon_url=manga.image_url)
            embeds.append(e1)
        e.set_image(url=manga.image_url)
        e.set_footer(
            text=f'{manga.title_japanese} | {manga.mal_id} | {manga.score} stars', icon_url=manga.image_url)
        await ctx.send(embed=e)
        for i in embeds:
            await ctx.send(embed=i)
            time.sleep(0.5)


def setup(bot):
    bot.add_cog(AnimeandManga(bot))
