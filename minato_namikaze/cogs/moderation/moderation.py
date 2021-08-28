from os.path import join
from typing import Optional, Union

import discord
from discord.ext import commands

from ...lib import (Embed, ErrorEmbed, check_if_warning_system_setup,
                    get_roles, get_user, return_ban_channel,
                    return_warning_channel)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Some simple moderation commands'

    # setdelay
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

    # kick
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
        await ctx.message.delete()
        await ctx.guild.kick(user=member, reason=reason)

        embed = Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason)
        await ctx.send(embed=embed)

    # ban
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
        await ctx.message.delete()
        member = get_user(member, ctx)
        if ctx.message.author == member or ctx.message.author.id == member:
            await ctx.send(embed=ErrorEmbed(description='You **can\'t ban yourself**!'))
            return
        try:
            await ctx.guild.ban(user=member, reason=reason)
        except:
            await ctx.send(embed=ErrorEmbed(description='Can\'t ban the memeber. Please make sure **my role is at the top**!'), delete_after=4)
            return

        embed = ErrorEmbed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    # banlist
    @commands.command(
        name="banlist",
        description="Shows list of users who have been banned! Or position of a specified user who was banned!",
        usage="Optional[<member.id> or <member.mention> or <member.name.with.tag>]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def banlist(self, ctx, *, member: Optional[Union[str, int, discord.Member]]):
        banned_users = list(i for i in await ctx.guild.bans())
        if not member:
            if len(banned_users) == 0:
                await ctx.send(embed=Embed(description='There is **no-one who is banned**! :zero: people are **banned**'))
                return
            l_no = 0
            embed = []
            if len(banned_users) > 10:
                for i in range(len(banned_users)//10):
                    description = ''
                    for l in range(10):
                        try:
                            description += f'\n{l_no+1}. - **{banned_users[l_no].user}** : ID [ **{banned_users[l_no].user.id}** ] '
                            l_no += 1
                        except:
                            pass

                    e = ErrorEmbed(
                        title='Those who were banned are:',
                        description=description
                    )
                    embed.append(e)

                paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
                paginator.add_reaction('⏮️', "first")
                paginator.add_reaction('⏪', "back")
                paginator.add_reaction('🔐', "lock")
                paginator.add_reaction('⏩', "next")
                paginator.add_reaction('⏭️', "last")

                await paginator.run(embed)
            else:
                description = ''
                for k, i in enumerate(banned_users):
                    description += f'\n{k+1}. - **{i.user}** : ID [ **{banned_users[k].user.id}** ] '
                e = ErrorEmbed(
                    title='Those who were banned are:',
                    description=description
                )
                embed.append(e)
                await ctx.send(embed=e)
                return
        else:
            if member.isdigit():
                member = int(member)
            if isinstance(member, str):
                member_name, member_discriminator = member.split('#')

            n = 0
            for i, ban_entry in enumerate(banned_users):
                user = ban_entry.user
                e = ErrorEmbed(topic=f'About the ban {member}')
                if isinstance(member, str):
                    if (user.name, user.discriminator) == (member_name, member_discriminator):
                        if ban_entry.reason:
                            e.add_field(name='**Reason**',
                                        value=ban_entry.reason, inline=True)
                        e.add_field(name='**Position**',
                                    value=i+1, inline=True)
                        e.add_field(name='**Banned User Name**',
                                    value=ban_entry.user, inline=True)
                        e.set_thumbnail(url=ban_entry.user.avatar_url)
                        await ctx.channel.send(embed=e)
                        n += 1
                        return

                elif isinstance(member, int):
                    if user.id == int(member):
                        if ban_entry.reason:
                            e.add_field(name='**Reason**',
                                        value=ban_entry.reason, inline=True)
                        e.add_field(name='**Position**',
                                    value=i+1, inline=True)
                        e.add_field(name='**Banned User Name**',
                                    value=ban_entry.user, inline=True)
                        e.set_thumbnail(url=ban_entry.user.avatar_url)
                        await ctx.channel.send(embed=e)
                        n += 1
                        return

                else:
                    if user == member:
                        if ban_entry.reason:
                            e.add_field(name='**Reason**',
                                        value=ban_entry.reason, inline=True)
                        e.add_field(name='**Position**',
                                    value=i+1, inline=True)
                        e.add_field(name='**Banned User Name**',
                                    value=ban_entry.user, inline=True)
                        e.set_thumbnail(url=ban_entry.user.avatar_url)
                        await ctx.channel.send(embed=e)
                        n += 1
                        return
            if n == 0:
                await ctx.send(embed=ErrorEmbed(description=f'The **{member}** isn\'t there in the **ban list**'))
                return

    # Unban
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
        try:
            member = member.strip(' ').strip('\n')
        except:
            pass
        if member.isdigit():
            member = int(member)
        if ctx.message.author == member or ctx.message.author.id == member:
            await ctx.send(embed=ErrorEmbed(description='You **can\'t unban yourself**! '))
            return

        banned_users = await ctx.guild.bans()
        if isinstance(member, str):
            member_name, member_discriminator = member.split('#')

        # ask reason function
        async def reason(ctx):
            question = await ctx.send(
                ctx.message.author.mention,
                embed=Embed(
                    description='Would you like to give any **reason for this unban**? \nIf there isn\'t any reason then type **(no/skip)**'
                )
            )
            try:
                reason_content = await self.bot.wait_for('message', timeout=25, check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            except TimeoutError:
                await ctx.send('Okay! **There won\'t be any reason**.', delete_after=3)
            await question.delete()
            return reason_content.content.capitalize() if reason_content.content.lower() not in ('skip', 'no') else None

        n = 0
        for ban_entry in banned_users:
            user = ban_entry.user
            e = Embed(title='Unbanned!',
                      description=f'**Unbanned**: {user.mention}')
            if isinstance(member, str):
                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    reason_unban = await reason(ctx)
                    await ctx.guild.unban(user, reason=reason_unban)
                    await ctx.channel.send(embed=e)
                    n += 1
                    return

            elif isinstance(member, int):
                if user.id == int(member):
                    reason_unban = await reason(ctx)
                    await ctx.guild.unban(user, reason=reason_unban)
                    await ctx.channel.send(embed=e)
                    n += 1
                    return

            else:
                if user == member:
                    reason_unban = await reason(ctx)
                    await ctx.guild.unban(user, reason=reason_unban)
                    await ctx.channel.send(embed=e)
                    n += 1
                    return
        if n == 0:
            await ctx.send(embed=ErrorEmbed(description=f'The **{member}** isn\'t there in the **ban list**'))
            return

    @commands.command(
        name="purge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        '''A command which purges the channel it is called in'''
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
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
        await ctx.message.delete()
        member = get_user(member, ctx)
        e = ErrorEmbed(title='You have been warned!')
        e.add_field(name='**Responsible Moderator**:',
                    value=ctx.message.author.mention, inline=True)
        if reason:
            e.add_field(name='**Reason**:', value=reason, inline=True)

        warning_channel = _warning_channel(ctx)
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

        warning_channel = _warning_channel(ctx)
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
