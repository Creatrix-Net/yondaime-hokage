# Discord Imports
import re

import discord
from discord.ext import commands

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! h|m|s|d are valid arguments"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Some simple moderation commands'

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def setdelay(self, ctx, seconds: int):
        """Sets Slowmode Of A Channel"""
        currentslow = ctx.channel.slowmode_delay
        if currentslow == seconds:
            return await ctx.send(f"Sorry, But this channel already has {seconds} set as the delay! (I don't want to waste my api calls lmao)")
        message = f"Set the slowmode delay in this channel to {seconds} seconds!"
        if seconds == 0:
            message = f"Reset Slowmode of channel {ctx.channel.name}"
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"{message}")

    @commands.command(
        name="kick",
        description="A command which kicks a given user",
        usage="<user> [reason]",
    )
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        '''A command which kicks a given user'''
        await ctx.guild.kick(user=member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason)
        await ctx.send(embed=embed)

    @kick.error
    async def error_handler(ctx, error):
        if isinstance(error, BotMissingPermissions):
            await ctx.send(f"I need the permissions: {' '.join(error.missing_perms)}")

        else:
            raise error

    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        '''A command which bans a given user'''
        await ctx.guild.ban(user=member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @ban.error
    async def error_handler(ctx, error):
        if isinstance(error, BotMissingPermissions):
            await ctx.send(f"I need the permissions: {' '.join(error.missing_perms)}")

        else:
            raise error

    @commands.command(
        name="unban",
        description="A command which unbans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.Member, *, reason=None):
        '''A command which unbans a given user'''
        await ctx.guild.unban(member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} unbanned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="purge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        '''A command which purges the channel it is called in'''
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount+1} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=4)


def setup(bot):
    bot.add_cog(Moderation(bot))
