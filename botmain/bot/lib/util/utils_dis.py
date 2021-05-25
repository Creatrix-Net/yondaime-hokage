
from discord.ext import menus
import discord
import random
from asyncio import sleep as sl


class VotingMenu(menus.Menu):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.bot.owner = "[DHRUVA SHAW#0550](https://discord.com/users/571889108046184449/)"

    async def send_initial_message(self, ctx, channel):
        e = discord.Embed(title="I see you want vote!",
                          description=f"{ctx.author.mention}, maybe react with your choice :)")
        return await channel.send(embed=e)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_check_mark(self, payload):
        
        topgg =  '\n - **[TopGG](https://top.gg/bot/779559821162315787)** '
        Discordbotlist = '\n - **[Discordbotlist](https://discordbotlist.com/bots/minato-namikaze)**'
        Discordlist = '   \n - **[Discordlist.Space](https://discordlist.space/bot/779559821162315787/upvote)**'
        BotsForDiscord = '\n - **[BotsForDiscord](https://botsfordiscord.com/bot/779559821162315787/vote)**'
        Boats = '\n - **[Discord.Boats](https://discord.boats/bot/779559821162315787/vote)**'
        Space = '\n - **[Space Bots List](https://space-bot-list.xyz/bots/779559821162315787/vote)**'
        fateslist = '\n - **[Fates List](https://fateslist.xyz/bot/779559821162315787/vote)**'
        voidbots = '\n - **[Void Bots](https://voidbots.net/bot/779559821162315787/vote)**'
        bladebotlist = '\n - **[BladeBotList](https://bladebotlist.xyz/bot/779559821162315787/vote)**'
        
        e1 = discord.Embed(title="Thanks!",
            description=f"Thanks {self.ctx.author.mention}! Here's the links:{topgg}{Discordbotlist}{Discordlist}{BotsForDiscord}{Boats}{Space}{fateslist}{voidbots}{bladebotlist}\n**[DisbotList](https://disbotlist.xyz/bot/779559821162315787/vote)**"
        )
        await self.message.edit(content="", embed=e1)
        self.stop()

    @menus.button('\N{NEGATIVE SQUARED CROSS MARK}')
    async def on_stop(self, payload):
        e2 = discord.Embed(title="Sorry to see you go!",
                           description="Remember you can always re-run the command :)")
        self.stop()
        await self.message.edit(content="", embed=e2)
        await sl(5)
        await self.message.delete()


class WhoMenu(menus.Menu):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def send_initial_message(self, ctx, channel):
        e = discord.Embed(title="I see you want to know more!",
                          description=f"{ctx.author.mention}, click the checkmark for the Privacy Policy or the crossmark for just info!")
        return await channel.send(embed=e)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def on_add(self, payload):
        e1 = discord.Embed(title="Well, Heres The Policy :)",
                           description=f"Well well well, Nothing is stored! Really nothing is stored! All is based on internal cache provided by Discord! For more please visit [THIS LINK](https://dhruvacube.github.io/yondaime-hokage/privacy_policy)", color=discord.Colour.from_hsv(random.random(), 1, 1))
        await self.message.edit(content="", embed=e1)

    @menus.button('\N{NEGATIVE SQUARED CROSS MARK}')
    async def on_stop(self, payload):
        e2 = discord.Embed(title="Hey!", description=f"Hi, I'm {self.bot.user}, I am developed by {self.bot.owner}, Who is a great fan of me i.e. {self.bot.user} aka Yondaime Hokage!", color=discord.Colour.from_hsv(
            random.random(), 1, 1))

        await self.message.edit(content="", embed=e2)


class MenuSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, data):
        embed = discord.Embed(description="\n".join(item for item in data))
        return embed
