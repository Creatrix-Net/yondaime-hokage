from os.path import join
from typing import Optional, Union

import discord
from discord.ext import commands

from ...lib import (Embed, ErrorEmbed, check_if_warning_system_setup,
                    get_roles, get_user, return_warning_channel, return_ban_channel)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Some simple moderation commands'

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
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

        embed = Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason)
        await ctx.send(embed=embed)

    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[int, discord.Member], *, reason=None):
        '''A command which bans a given user'''
        member = get_user(member, ctx)
        await ctx.guild.ban(user=member, reason=reason)

        embed = ErrorEmbed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)
        if reason:
            await return_ban_channel(ctx, ctx.guild).send(ErrorEmbed(description=reason))

    @commands.command(
        name="unban",
        description="A command which unbans a given user",
        usage="<user> [reason]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def unban(self, ctx, *, member: Union[str, int, discord.Member]):
        '''A command which unbans a given user'''
        await ctx.message.delete()
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            e = Embed(title='Unbanned!',
                      description=f'**Unbanned**: {user.mention}')
            if isinstance(member, str):
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.channel.send(embed=e)
            elif isinstance(member, int):
                if user.id == int(member):
                    await ctx.guild.unban(user)
                    await ctx.channel.send(embed=e)
            else:
                if user == member:
                    await ctx.guild.unban(user)
                    await ctx.channel.send(embed=e)

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
        embed = Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=4)

    @commands.command(pass_context=True, usage="<member.mention> <role>", alias=['add_roles'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def ar(self, ctx, member: Optional[Union[int, discord.Member]], role: Union[int, discord.Role]):
        '''Add roles'''
        member = get_user(member if member !=
                          None else ctx.message.author, ctx)
        role = get_roles(role, ctx)
        await member.add_roles(role)
        e = Embed(
            title="Added Roles", description=f"I have added the roles '{role.mention}' for {member.mention}!"
        )
        await ctx.send(embed=e)

    @commands.command(pass_context=True, usage='<member.mention> <optional: reason>')
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.check(check_if_warning_system_setup)
    async def warn(self, ctx, member: Union[int, discord.Member], *, reason: str = None):
        '''Warn a user'''
        member = get_user(member, ctx)
        e = ErrorEmbed(title='You have been warned!')
        e.add_field(name='**Responsible Moderator**:',
                    value=ctx.message.author.mention, inline=True)
        if reason:
            e.add_field(name='**Reason**:', value=reason, inline=True)

        warning_channel = return_warning_channel(ctx)
        await member.send(embed=e)
        await warning_channel.send(embed=e, content=member.mention)
        await ctx.send(f'{member.mention} has been **warned** by you ||{ctx.author.mention}||', delete_after=10)

    @warn.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            e = ErrorEmbed(
                title=f'No warning system setup for the {ctx.guild.name}',
                description='You can always setup the **warning system** using `)setup` command'
            )
            await ctx.send(embed=e)

    @commands.command(pass_context=True, usage='<member.mention>')
    @commands.guild_only()
    @commands.check(check_if_warning_system_setup)
    async def warnlist(self, ctx, member: Optional[Union[int, discord.Member]] = None):
        '''Get the no. of warns for a specified user'''
        member = get_user(member if member !=
                          None else ctx.message.author, ctx)
        e = Embed(title='Type the below message in the search bar')
        search_image = discord.File(
            join(self.bot.minato_dir, 'discord', 'search.png'), filename='search.png')
        e.set_image(url="attachment://search.png")
        await ctx.send(file=search_image, embed=e)

        warning_channel = return_warning_channel(ctx)
        message = f'mentions: {member}  in: {warning_channel}'
        await ctx.send(message)

    @warnlist.error
    async def warnlist_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            e = ErrorEmbed(
                title=f'No warning system setup for the {ctx.guild.name}',
                description='You/Admin can always setup the **warning system** using `)setup` command'
            )
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Moderation(bot))
