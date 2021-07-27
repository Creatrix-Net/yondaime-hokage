from discord.ext import commands
from mal import AnimeSearch
from ...lib import Embed
import DiscordUtils

class AnimeMangaandWaifu(commands.Cog, name='Anime, Manga and Waifu'):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Some anime and waifu related commands (vote locked).'
    
    @commands.command(
        description='Searches Anime from MAL and displayes the first 10 search result.',
        usage='<anime.name>',
        aliases=['anisearch', 'animesearchbyname', 'anime_search_by_name', 'searchanime', 'searchani']
        )
    async def animesearch(self, ctx, *, anime_name: str):
        '''Searches Anime from MAL and displayes the first 10 search result.'''
        search = AnimeSearch(str(anime_name).strip(' ').lower())
        search_results = search.results[:10]
        description = ''
        for i,k in enumerate(search_results):
            description+=f'{i+1}. **{k.title}**\n'
        e1=Embed(
            title=f'Anime search results for {str(anime_name).capitalize()}',
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
            e.add_field(name='**Anime Type**', value=i.type)
            e.add_field(name='**MAL Url**', value=f'[CLICK HERE]({i.url})')
            e.add_field(name='**MAL ID**', value=i.mal_id)
            e.set_image(url=i.image_url)
            e.set_footer(text=f'{i.title} | {i.mal_id} | {i.score} stars', icon_url=i.image_url)
            embeds.append(e)
        
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx) 
        await paginator.run(embeds)
    


def setup(bot):
    bot.add_cog(AnimeMangaandWaifu(bot))
