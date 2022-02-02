import asyncio
from typing import Optional

import discord
from asyncdagpi import Client
from discord.ext import commands
from mal import Anime, AnimeSearch, Manga, MangaSearch

from lib import (
    Embed,
    EmbedPaginator,
    ErrorEmbed,
    Tokens,
)


def format_related_anime_manga(dict_related_anime):
    formatted_string = "\n"
    for i in dict_related_anime:
        formatted_string += (
            f'・**{i.capitalize()}**: {" ,".join(dict_related_anime[i])} ;\n')
    return formatted_string


def format_staff(staff):
    staff_string = "\n"
    for k in staff:
        staff_string += f"・**{k.name}**: {k.role}\n"
    return staff_string


def format_characters(character):
    character_string = "\n"
    for k in character:
        character_string += f"・**{k.name}** \n@role: **{k.role}** \nVoice Actor: **{k.voice_actor}**\n\n"
    return character_string


def format_manga_characters(character):
    character_string = "\n"
    for k in character:
        character_string += f"・**{k.name}** \n@role: **{k.role}**\n\n"
    return character_string


class AnimeaMangaandWaifu(commands.Cog, name="Anime, Manga and Waifu"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.dagpi = Client(Tokens.dagpi.value)
        self.description = "Some anime, manga and waifu related commands (vote locked)."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="anime", id=874922782964731934)

    async def get_waifu(self):
        waifu = await self.bot.dagpi.waifu()
        pic = waifu["display_picture"]
        name = waifu["name"]
        likes_rank = waifu["like_rank"]
        trash_rank = waifu["trash_rank"]
        anime = waifu["appearances"][0]["name"]
        url = waifu["url"]

        e = Embed(title=name)
        e.add_field(name="**Anime**", value=anime, inline=True)
        e.add_field(name="**:heartbeat:**", value=likes_rank, inline=True)
        e.add_field(name="**:wastebasket:**", value=trash_rank, inline=True)
        e.add_field(name="**:link:**", value=f"[Know More]({url})")
        e.set_image(url=pic)
        e.set_footer(text="React with any emoji in 30 sec to claim him/her")
        return e, name

    # search anime
    @commands.command(
        description="Searches Anime from MAL and displays the first 10 search result. (vote locked)",
        usage="<anime.name>",
        aliases=[
            "anisearch",
            "animesearchbyname",
            "anime_search_by_name",
            "searchanime",
            "searchani",
        ],
    )
    async def animesearch(self, ctx, *, anime_name: str):
        """Searches Anime from MAL and displays the first 10 search result. (vote locked)"""
        search = AnimeSearch(str(anime_name).strip(" ").lower())
        search_results = search.results[:10]
        description = ""
        for i, k in enumerate(search_results):
            description += f"{i+1}. **{k.title}**\n"
        e1 = Embed(
            title=f"Anime search results for {str(anime_name).capitalize()}",
            description=description[:4096],
            timestamp=ctx.message.created_at,
        )
        e1.set_footer(
            text=f"Showing 10 results out of {len(search.results)} | Use the recations of this message to paginate",
            icon_url="https://cdn.myanimelist.net/images/event/15th_anniversary/top_page/item7.png",
        )
        embeds = [e1]
        for i in search_results:
            e = Embed(title=i.title,
                      description=i.synopsis,
                      timestamp=ctx.message.created_at)
            if i.score:
                e.add_field(name="**Score**", value=f"{i.score} :star:")
            if i.type:
                e.add_field(name="**Anime Type**", value=i.type)
            if i.url:
                e.add_field(name="**MAL Url**", value=f"[CLICK HERE]({i.url})")
            if i.mal_id:
                e.add_field(name="**MAL ID**", value=i.mal_id)
            if i.image_url:
                e.set_image(url=i.image_url)
            e.set_footer(text=f"{i.title} | {i.mal_id} | {i.score} stars",
                         icon_url=i.image_url)
            embeds.append(e)

        paginator = EmbedPaginator(entries=embeds, ctx=ctx)
        await paginator.start()

    # about anime
    @commands.command(
        description="Displays about the anime using the MAL ANIME ID. get it by using animesearch command. (vote locked)",
        usage="<mal.id>",
        aliases=[
            "aniabout",
            "animeabout",
            "anime_about_by_mal_id",
            "knowanime",
            "aboutani",
            "anime",
        ],
    )
    async def aboutanime(self, ctx, mal_id: int):
        """Displays about the anime using the MAL ANIME ID. get it by using animesearch command. (vote locked)"""
        await ctx.send(":mag: Searching...", delete_after=5)
        anime = Anime(int(mal_id))
        embeds = []
        e = Embed(
            title=anime.title,
            description=anime.synopsis[:4096],
            timestamp=ctx.message.created_at,
        )
        if anime.title_japanese:
            e.add_field(
                name=":japanese_castle: **Title in Japanese**",
                value=f"{anime.title_japanese}",
            )
        if anime.title_synonyms:
            e.add_field(name="**Title Synonyms**",
                        value=" ,".join(anime.title_synonyms))
        if anime.score:
            e.add_field(name=":star: **Score**", value=f"{anime.score} :star:")
        if anime.type:
            e.add_field(name=":dividers: **Type**", value=anime.type)
        if anime.url:
            e.add_field(name=":link: **MAL Url**",
                        value=f"[CLICK HERE]({anime.url})")
        if anime.mal_id:
            e.add_field(name=":id: **MAL ID**", value=anime.mal_id)
        if anime.status:
            e.add_field(name=":hourglass_flowing_sand: **Status**",
                        value=anime.status)
        if anime.genres:
            e.add_field(name=":arrow_right: **Genre**",
                        value=" ,".join(anime.genres))
        if anime.rank:
            e.add_field(name=":trophy: **Rank**", value=anime.rank)
        if anime.popularity:
            e.add_field(name="**Popularity**", value=f"#{anime.popularity}")
        if anime.episodes:
            e.add_field(name=":minidisc: **No. of Episodes**",
                        value=anime.episodes)
        if anime.premiered:
            e.add_field(name="**Premire(d)**", value=anime.premiered)
        if anime.aired:
            e.add_field(name=":calendar_spiral: **Air(ed/ing)**",
                        value=anime.aired)
        if anime.broadcast:
            e.add_field(name="**Broadcast**", value=anime.broadcast)
        if anime.producers:
            e.add_field(name="**Producers**", value=" ,".join(anime.producers))
        if anime.licensors:
            e.add_field(name="**Licensors**", value=" ,".join(anime.licensors))
        if anime.studios:
            e.add_field(name=":microphone2: **Studios**",
                        value=" ,".join(anime.studios))
        if anime.source:
            e.add_field(name=":information_source: **Source**",
                        value=anime.source)
        if anime.duration:
            e.add_field(name=":stopwatch: **Duration**", value=anime.duration)
        if anime.rating:
            e.add_field(name="**Rating**", value=anime.rating)
        if (anime.related_anime and
                len(format_related_anime_manga(anime.related_anime)) < 1024):
            e.add_field(
                name="**Related Anime**",
                value=format_related_anime_manga(anime.related_anime),
            )
        else:
            if anime.related_anime:
                e1 = Embed(
                    title="Related Anime",
                    description=format_related_anime_manga(
                        anime.related_anime)[:4096],
                )
                e1.set_footer(
                    text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
                    icon_url=anime.image_url,
                )
                embeds.append(e1)
        if anime.opening_themes and len(" ,".join(
                anime.opening_themes)) <= 1000:
            e.add_field(
                name=":play_pause: **Opening Theme(s)**",
                value="・\n".join(anime.opening_themes),
            )
        else:
            if anime.opening_themes:
                e1 = Embed(
                    title=":play_pause: Opening Theme(s)",
                    description="・\n".join(anime.opening_themes)[:4096],
                )
                e1.set_footer(
                    text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
                    icon_url=anime.image_url,
                )
                embeds.append(e1)
        if anime.ending_themes and len(" ,".join(anime.ending_themes)) <= 1000:
            e.add_field(
                name=":stop_button: **Ending Theme(s)**",
                value="・\n".join(anime.ending_themes),
            )
        else:
            if anime.ending_themes:
                e1 = Embed(
                    title=":stop_button: Ending Theme(s)",
                    description="・\n".join(anime.ending_themes)[:4096],
                )
                e1.set_footer(
                    text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
                    icon_url=anime.image_url,
                )
                embeds.append(e1)
        if anime.staff and len(format_staff(anime.staff)) <= 700:
            e.add_field(name=":factory_worker: Staff",
                        value=format_staff(anime.staff))
        else:
            if anime.staff:
                e1 = Embed(
                    title=":factory_worker: Staff",
                    description=format_staff(anime.staff)[:4096],
                )
                e1.set_footer(
                    text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
                    icon_url=anime.image_url,
                )
                embeds.append(e1)
        if anime.characters and len(format_characters(
                anime.characters)) <= 600:
            e.add_field(name="**Characters**",
                        value=format_characters(anime.characters))
        else:
            if anime.characters:
                e1 = Embed(
                    title="Characters",
                    description=format_characters(anime.characters)[:4096],
                )
                e1.set_footer(
                    text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
                    icon_url=anime.image_url,
                )
                embeds.append(e1)
        if anime.image_url:
            e.set_image(url=anime.image_url)
        e.set_footer(
            text=f"{anime.title_japanese} | {anime.mal_id} | {anime.score} stars",
            icon_url=anime.image_url,
        )
        paginator = EmbedPaginator(entries=[e] + embeds, ctx=ctx)
        await paginator.start()

    # search manga
    @commands.command(
        description="Searches Manga from MAL and displays the first 10 search result. (vote locked)",
        usage="<manga.name>",
        aliases=[
            "magsearch",
            "mangasearchbyname",
            "manga_search_by_name",
            "searchmanga",
            "searchmag",
        ],
    )
    async def mangasearch(self, ctx, *, manga_name: str):
        """Searches Manga from MAL and displays the first 10 search result. (vote locked)"""
        search = MangaSearch(str(manga_name).strip(" ").lower())
        search_results = search.results[:10]
        description = ""
        for i, k in enumerate(search_results):
            description += f"{i+1}. **{k.title}**\n"
        e1 = Embed(
            title=f"Manga search results for {str(manga_name).capitalize()}",
            description=description,
            timestamp=ctx.message.created_at,
        )
        e1.set_footer(
            text=f"Showing 10 results out of {len(search.results)} | Use the recations of this message to paginate",
            icon_url="https://cdn.myanimelist.net/images/event/15th_anniversary/top_page/item7.png",
        )
        embeds = [e1]
        for i in search_results:
            e = Embed(title=i.title,
                      description=i.synopsis,
                      timestamp=ctx.message.created_at)
            if i.score:
                e.add_field(name="**Score**", value=f"{i.score} :star:")
            if i.type:
                e.add_field(name="**Manga Type**", value=i.type)
            if i.url:
                e.add_field(name="**MAL Url**", value=f"[CLICK HERE]({i.url})")
            if i.mal_id:
                e.add_field(name="**MAL ID**", value=i.mal_id)
            if i.image_url:
                e.set_image(url=i.image_url)
            e.set_footer(text=f"{i.title} | {i.mal_id} | {i.score} stars",
                         icon_url=i.image_url)
            embeds.append(e)

        paginator = EmbedPaginator(entries=embeds, ctx=ctx)
        await paginator.start()

    # about manga
    @commands.command(
        description="Displays about the manga using the MAL MANGA ID. get it by using mangasearch command. (vote locked)",
        usage="<mal.id>",
        aliases=[
            "magabout",
            "mangaabout",
            "manga_about_by_mal_id",
            "knowmanga",
            "aboutmag",
            "manga",
        ],
    )
    async def aboutmanga(self, ctx, mal_id: int):
        """Displays about the manga using the MAL MANGA ID. get it by using mangasearch command. (vote locked)"""
        message = await ctx.send(":mag: Searching...", delete_after=5)
        manga = Manga(int(mal_id))
        embeds = []
        e = Embed(
            title=manga.title,
            description=manga.synopsis[:4096],
            timestamp=ctx.message.created_at,
        )
        if manga.title_japanese:
            e.add_field(
                name=":japanese_castle: **Title in Japanese**",
                value=f"{manga.title_japanese}",
            )
        if manga.title_synonyms:
            e.add_field(name="**Title Synonyms**",
                        value=" ,".join(manga.title_synonyms))
        if manga.score:
            e.add_field(name=":star: **Score**", value=f"{manga.score} :star:")
        if manga.type:
            e.add_field(name=":dividers: **Type**", value=manga.type)
        if manga.url:
            e.add_field(name=":link: **MAL Url**",
                        value=f"[CLICK HERE]({manga.url})")
        if manga.mal_id:
            e.add_field(name=":id: **MAL ID**", value=manga.mal_id)
        if manga.status:
            e.add_field(name=":hourglass_flowing_sand: **Status**",
                        value=manga.status)
        if manga.genres:
            e.add_field(name=":arrow_right: **Genre**",
                        value=" ,".join(manga.genres))
        if manga.rank:
            e.add_field(name=":trophy: **Rank**", value=manga.rank)
        if manga.popularity:
            e.add_field(name="**Popularity**", value=f"#{manga.popularity}")
        if manga.chapters:
            e.add_field(name=":book: **No. of Chapters**",
                        value=manga.chapters)
        if manga.volumes:
            e.add_field(name=":books: **Volumes**", value=manga.volumes)
        if manga.authors:
            e.add_field(name=":pen_fountain: **Author(s)**",
                        value="\n・".join(manga.authors))
        if manga.published:
            e.add_field(name=":map: **Published**", value=manga.published)
        if manga.characters and len(format_manga_characters(
                manga.characters)) <= 600:
            e.add_field(name="**Characters**",
                        value=format_manga_characters(manga.characters))
        else:
            if manga.characters:
                e1 = Embed(
                    title="Characters",
                    description=format_manga_characters(
                        manga.characters)[:4096],
                )
                e1.set_footer(
                    text=f"{manga.title_japanese} | {manga.mal_id} | {manga.score} stars",
                    icon_url=manga.image_url,
                )
                embeds.append(e1)
        if (manga.related_manga and
                len(format_related_anime_manga(manga.related_manga)) < 1024):
            e.add_field(
                name="**Related Manga**",
                value=format_related_anime_manga(manga.related_manga),
            )
        else:
            if manga.related_manga:
                e1 = Embed(
                    title="Related Manga",
                    description=format_related_anime_manga(
                        manga.related_manga)[:4096],
                )
                e1.set_footer(
                    text=f"{manga.title_japanese} | {manga.mal_id} | {manga.score} stars",
                    icon_url=manga.image_url,
                )
                embeds.append(e1)
        if manga.image_url:
            e.set_image(url=manga.image_url)
        e.set_footer(
            text=f"{manga.title_japanese} | {manga.mal_id} | {manga.score} stars",
            icon_url=manga.image_url,
        )
        paginator = EmbedPaginator(entries=[e] + embeds, ctx=ctx)
        await paginator.start()

    @commands.command(aliases=["w", "wfu", "wa"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def waifu(self, ctx):
        """Get random waifu and marry them! UwU! (vote locked)"""
        async with ctx.typing():
            waifu = await self.get_waifu()
            message = await ctx.send(embed=waifu[0])
            await message.add_reaction(discord.PartialEmoji(name="\U0001f493"))

        def check(reaction, user):
            return user != self.bot.user and message.id == reaction.message.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add",
                                                     timeout=30.0,
                                                     check=check)
            await ctx.send(
                f":sparkling_heart: **{user.mention}** has *married* **{waifu[-1]}**! UwU :ring:"
            )
        except asyncio.TimeoutError:
            pass

    @commands.command(aliases=["wtp", "whatsthatpokemon"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def whosthatpokemon(self, ctx):
        """Play Who\'s That Pokemon? (vote locked)"""
        async with ctx.typing():
            wtp = await self.bot.dagpi.wtp()
            question = wtp.question
            answer = wtp.name.lower()

            e = Embed(title="Who's That Pokemon?",
                      timestamp=ctx.message.created_at)
            e.set_footer(
                text=f"{ctx.message.author} reply within 30secs to answer.",
                icon_url=ctx.message.author.avatar.url,
            )
            e.set_image(url=question)

            question_message = await ctx.send(
                "You have 3 chances, **Chance: 1/3**", embed=e)

        answerembed = discord.Embed(
            title=f"The Pokemon is: {wtp.name.capitalize()}",
            description=f"```Here is the Info\n\nAbilities: {', '.join(list(map(lambda x: x.capitalize(),wtp.abilities)))}```",
            timestamp=ctx.message.created_at,
        )
        answerembed.add_field(name="**Height**", value=f"{round(wtp.height)}m")
        answerembed.add_field(name="**Weight**",
                              value=f"{round(wtp.weight)} kg")
        answerembed.add_field(name=":id:", value=wtp.id)
        answerembed.set_image(url=wtp.answer)
        answerembed.set_footer(text=wtp.name.capitalize(), icon_url=wtp.answer)
        answerembed.set_author(name=wtp.name.capitalize(),
                               url=wtp.link,
                               icon_url=wtp.answer)
        for i in range(3):
            try:
                answer_content = await self.bot.wait_for(
                    "message",
                    timeout=30,
                    check=lambda m: m.author == ctx.author and m.channel == ctx
                    .channel,
                )
                await asyncio.sleep(0.8)
                if answer_content.content.lower() != answer:
                    try:
                        await answer_content.delete()
                    except:
                        pass
                    await ctx.send(
                        embed=ErrorEmbed(
                            description="Please try again! :no_entry:"),
                        delete_after=3,
                    )
                    await question_message.edit(
                        content=f"You have {3-(i+1)} chances, **Chance: {i+1}/3**",
                        embed=e,
                    )
                    pass
                elif answer_content.content.lower() == answer:
                    try:
                        await answer_content.delete()
                    except:
                        pass
                    answerembed.color = discord.Color.green()
                    await question_message.edit(
                        content=f"**Yes you guessed it right!** in {i+1} chance(s), {ctx.author.mention}",
                        embed=answerembed,
                    )
                    return
                elif i + 1 == 3 and answer_content.content.lower() != answer:
                    try:
                        await answer_content.delete()
                    except:
                        pass
                    answerembed.color = discord.Color.red()
                    await question_message.edit(
                        content=f"Well you couldn't **guess it right in 3 chances**. Here is your **answer**!, {ctx.author.mention}",
                        embed=answerembed,
                    )
                    return
            except TimeoutError:
                try:
                    await answer_content.delete()
                except:
                    pass
                await ctx.send(embed=ErrorEmbed(
                    description="Well you didn't atleast once.\n Thus I won't be telling you the answer! :rofl:. **Baka**"
                ))
                return
        try:
            await answer_content.delete()
        except:
            pass
        answerembed.color = discord.Color.red()
        await question_message.edit(
            content=f"Well you couldn't **guess it right in 3 chances**. Here is your **answer**!, {ctx.author.mention}",
            embed=answerembed,
        )
        return


def setup(bot):
    bot.add_cog(AnimeaMangaandWaifu(bot))
