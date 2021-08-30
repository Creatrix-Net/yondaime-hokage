import re

import discord
from discord.ext import commands

invitere = r"(?:https?:\/\/)?discord(?:\.gg|app\.com\/invite)?\/(?:#\/)([a-zA-Z0-9-]*)"
invitere2 = r"(http[s]?:\/\/)*discord((app\.com\/invite)|(\.gg))\/(invite\/)?(#\/)?([A-Za-z0-9\-]+)(\/)?"


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}
        self.description = '"Snipes" someone\'s message that\'s been edited or deleted.'

        @bot.listen('on_message_delete')
        async def on_message_delete(msg):
            if msg.author.bot:
                return
            self.snipes[msg.channel.id] = msg

        @bot.listen('on_message_edit')
        async def on_message_edit(before, after):
            if before.author.bot or after.author.bot:
                return  # DEPARTMENT OF REDUNDANCY DEPARTMENT
            if (self.eval(before.content, after.content) >= 10) and (
                    len(before.content) > len(after.content)):
                self.snipes[before.channel.id] = [before, after]
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{DIRECT HIT}')

    def sanitise(self, string):
        if len(string) > 1024:
            string = string[0:1021] + "..."
        string = re.sub(invitere2, '[INVITE REDACTED]', string)
        return string

    def minDis(self, s1, s2, n, m, dp):
        # If any string is empty,
        # return the remaining characters of other string
        if(n == 0):
            return m
        if(m == 0):
            return n

        # To check if the recursive tree
        # for given n & m has already been executed
        if(dp[n][m] != -1):
            return dp[n][m]

        # If characters are equal, execute
        # recursive function for n-1, m-1
        if(s1[n - 1] == s2[m - 1]):
            if(dp[n - 1][m - 1] == -1):
                dp[n][m] = self.minDis(s1, s2, n - 1, m - 1, dp)
                return dp[n][m]
            else:
                dp[n][m] = dp[n - 1][m - 1]
                return dp[n][m]

        # If characters are nt equal, we need to
        # find the minimum cost out of all 3 operations.
        else:
            if(dp[n - 1][m] != -1):
                m1 = dp[n - 1][m]
            else:
                m1 = self.minDis(s1, s2, n - 1, m, dp)

            if(dp[n][m - 1] != -1):
                m2 = dp[n][m - 1]
            else:
                m2 = self.minDis(s1, s2, n, m - 1, dp)
            if(dp[n - 1][m - 1] != -1):
                m3 = dp[n - 1][m - 1]
            else:
                m3 = self.minDis(s1, s2, n - 1, m - 1, dp)

            dp[n][m] = 1 + min(m1, min(m2, m3))
            return dp[n][m]

    def eval(self, str1, str2):
        n = len(str1)
        m = len(str2)
        dp = [[-1 for i in range(m + 1)] for j in range(n + 1)]
        return self.minDis(str1, str2, n, m, dp)

    @commands.command()
    async def snipe(self, ctx):
        '"Snipes" someone\'s message that\'s been edited or deleted.'
        try:
            snipe = self.snipes[ctx.channel.id]
        except KeyError:
            return await ctx.send('No snipes in this channel!')
        if snipe is None:
            return await ctx.send('No snipes in this channel!')
        emb = discord.Embed()
        if type(snipe) == list:  # edit snipe
            emb.set_author(
                name=str(snipe[0].author),
                icon_url=snipe[0].author.avatar_url)
            emb.colour = snipe[0].author.colour
            emb.add_field(
                name='Before',
                value=self.sanitise(snipe[0].content),
                inline=False)
            emb.add_field(
                name='After',
                value=self.sanitise(snipe[1].content),
                inline=False)
            emb.timestamp = snipe[0].created_at
        else:  # delete snipe
            emb.set_author(
                name=str(snipe.author),
                icon_url=snipe.author.avatar_url)
            emb.description = self.sanitise(snipe.content)
            emb.colour = snipe.author.colour
            emb.timestamp = snipe.created_at
        emb.set_footer(
            text=f'Message sniped by {str(ctx.author)}',
            icon_url=ctx.author.avatar_url)
        await ctx.send(embed=emb)
        self.snipes[ctx.channel.id] = None


def setup(bot):
    bot.add_cog(Snipe(bot))
