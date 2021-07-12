import discord
from discord.ext import commands
from ...lib.classes.games import *
from ...lib import Embed, ErrorEmbed
import time

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Play some amazing games"
    
    @commands.command(aliases=['tc'], usage='<other player.mention>')
    @commands.guild_only()
    async def tictactoe(self, ctx, member: discord.Member):
        '''Play Amazing Tictactoe Game'''
        if member == ctx.author or member.bot:
            await ctx.send(embed=ErrorEmbed(description='*You cannot play this game yourself or with a bot*'))
            return
        await ctx.send(
            embed=Embed(
                description=f'*Positions are marked with 1,2,3.. just like 3x3 cube*\n{ctx.author.mention} you are taking *cross*\n{member.mention} you are taking *circle*'
                )
            )
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
            await ctx.send(embed=ErrorEmbed(description='*You cannot play this game yourself or with a bot*'))
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
        '''Play Hangman!'''
        await ctx.send('**Here is the link to know about** *Hangman*:')
        await ctx.send('<https://en.wikipedia.org/wiki/Hangman_(game)#Example_game>')
        
        await ctx.send('__After execution__ of **hangman** command *reply* to the embed *to guess the word/movie.*')
        game = hangman.Hangman()
        await game.start(ctx)
    
    
    @commands.command(aliases=['aki'])
    async def akinator(self, ctx):
        '''Play Akinator'''
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

def setup(bot):
    bot.add_cog(Games(bot))
