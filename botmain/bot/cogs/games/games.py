import discord
from discord.ext import commands
from Discord_Games import connect_four, tictactoe, hangman, twenty_48, aki, ChessGame


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Play some amazing games"
    
    @commands.command(aliases=['tc'])
    @commands.guild_only()
    async def tictactoe(self, ctx, member: discord.Member, usage='<other player.mention>'):
        '''Play Amazing Tictactoe Game'''
        if member == ctx.author or member.bot:
            await ctx.send('*You cannot play this game yourself or with a bot*')
            return
        await ctx.send('*Positions are marked with 1,2,3.. just like 3x3 cube*')
        await ctx.send(f'{ctx.author.mention} you are taking *cross*')
        await ctx.send(f'{member.mention} you are taking *circle*')
        game = tictactoe.Tictactoe(
            cross  = ctx.author,   
            circle = member,
        )
        await game.start(ctx, remove_reaction_after=True)
    
    @commands.command(aliases=['connect_four','c4','cf'], usage='<other player.mention>')
    @commands.guild_only()
    async def connectfour(self, ctx, member: discord.Member):
        '''Play Amazing Connect Four Game'''
        if member == ctx.author or member.bot:
            await ctx.send('*You cannot play this game yourself or with a bot*')
            return
        await ctx.send('**Here is the link to know about** *Connect Four*:')
        await ctx.send('<https://en.wikipedia.org/wiki/Connect_Four#firstHeading>')
        await ctx.send(f'{ctx.author.mention} you are taking *red*')
        await ctx.send(f'{member.mention} you are taking *blue*')
        game = connect_four.ConnectFour(
            red  = ctx.author,   
            blue = member,
        )
        await game.start(ctx, remove_reaction_after=True)
    
    @commands.command(aliases=['hg'])
    async def hangman(self, ctx):
        '''Play hangman'''
        await ctx.send('**Here is the link to know about** *Hangman*:')
        await ctx.send('<https://en.wikipedia.org/wiki/Hangman_(game)#Example_game>')
        '''Play Hangman'''
        await ctx.send('__After execution__ of **hangman** command *reply* to the embed *to guess the word/movie.*')
        game = hangman.Hangman()
        await game.start(ctx)
    
    @commands.command(aliases=['aki'])
    async def akinator(self, ctx):
        '''Play Akinator'''
        import time
        await ctx.send('**Here is the link to know about** *Akinator*:')
        await ctx.send('<https://en.wikipedia.org/wiki/Akinator#Gameplay>')
        a = await ctx.send('**Now get ready for the game**')
        time.sleep(1)
        await a.edit(content='Starting in 5 seconds')
        for i in range(4):
            await a.edit(content=4-i)
            time.sleep(1)
        await a.delete()
        game = aki.Akinator()
        await game.start(ctx)
    
    @commands.command(aliases=['2048','t48'])
    async def twenty_48(self, ctx):
        '''Play 20487 Game'''
        await ctx.send('**Here is the link to know about** *2048*:')
        await ctx.send('<https://en.wikipedia.org/wiki/2048_(video_game)#Gameplay>')
        game = twenty_48.Twenty48()
        await game.start(ctx, remove_reaction_after = True, delete_button = False, embed = discord.Embed())
    
    @commands.command(usage='<other player.mention>')
    @commands.guild_only()
    async def chess(self, ctx, member: discord.Member):
        '''Play Chess with your partner'''
        if member == ctx.author or member.bot:
            await ctx.send('*You cannot play this game yourself or with a bot*')
            return
        await ctx.send('**Here is the rules of the** *Chess*:')
        await ctx.send('<https://en.wikipedia.org/wiki/Rules_of_chess#Gameplay>')
        await ctx.send('--------')
        await ctx.send(f'{ctx.author.mention} you are taking the *White Pieces*')
        await ctx.send(f'{member.mention} you are taking the *Black Pieces*')
        game = ChessGame.Chess(
            white=ctx.author,
            black=member
        )
        await game.start(ctx)



def setup(bot):
    bot.add_cog(Games(bot))