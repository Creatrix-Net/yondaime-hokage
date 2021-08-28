from typing import Optional, Union

import discord
import DiscordUtils
from discord.ext import commands

from ...lib import (Embed, ErrorEmbed, check_if_support_is_setup, get_user,
                    return_support_channel)


def if_inside_support_channel(ctx):
    if check_if_support_is_setup(ctx):
        if ctx.message.channel == return_support_channel(ctx):
            return True
        else:
            return False
    else:
        return False


def errorembed(ctx):
    return ErrorEmbed(
        title=f'No support system setup for the {ctx.guild.name}',
        description='An admin can always setup the **support system** using `)setup` command'
    )


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Displays the support command for the server, this can only be used if the server owner has enabled it.'

    @commands.command(description='Open support ticket if enabled by the server admins')
    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.check(check_if_support_is_setup)
    @commands.guild_only()
    async def support(self, ctx):
        '''Open support ticket if enabled by the server admins'''
        chan = return_support_channel(ctx)

        if ctx.message.author == ctx.guild.owner:
            await ctx.send(f'{ctx.message.author.mention} really you need support ??! **LOL !** :rofl:')
            return
        elif chan == ctx.message.channel:
            await ctx.send(embed=ErrorEmbed(description=f'{ctx.message.author.mention} This command can\'t be run inside the {chan.mention}'), delete_after=4)
            return
        elif discord.utils.get(ctx.guild.roles, name="SupportRequired") in ctx.message.author.roles:
            await ctx.send(embed=ErrorEmbed(description=f'{ctx.message.author.mention} you already applied for the support , please check the {chan.mention} channel.'))
            return
        else:
            channel = ctx.channel
            await ctx.message.author.add_roles(discord.utils.get(ctx.guild.roles, name="SupportRequired"))
            if channel.guild is ctx.guild:
                per = ctx.author.mention
                e = Embed(
                    title='Help Required',
                    description=f"{per} in {channel.mention} needs support!"
                )
                await chan.send("@here", embed=e)
                await ctx.send(f"**Help Desk** has been has been notifed!")
                e = Embed(
                    title='Support Requirement Registered',
                    description=f'Your need for the support in **{ctx.guild.name}** has been registered'
                )
                await ctx.message.author.send('Hello', embed=e)
                return

    @support.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure) and not isinstance(error, commands.MissingPermissions) and not isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=errorembed(ctx))

    @commands.command(description='Resolves the existing ticket!', usage='<member.mention>')
    @commands.check(if_inside_support_channel)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def resolved(self, ctx, member: Union[int, discord.Member]):
        '''Resolves the existing ticket!'''
        member = get_user(member, ctx)
        if member.bot:
            await ctx.send(embed=ErrorEmbed(description=f'{member.mention} is a bot! :robot:'))
            return
        elif not discord.utils.get(ctx.guild.roles, name="SupportRequired") in member.roles:
            e = ErrorEmbed(
                title='Sorry !',
                description=f'{member.mention} has not requested any **support** !'
            )
            await ctx.send(embed=e)
            return

        await member.send(f'Hope your issue has been resolved in {ctx.guild.name}, {member.mention}')
        await ctx.send(f'The issue/query for {member.mention} has been set to resolved!')
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="SupportRequired"))

    @resolved.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure) and not isinstance(error, commands.MissingPermissions) and not isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=ErrorEmbed(description='This command can be run **inside only servers\'s support channel**.'))

    @commands.command(description='Checks who still requires the support.', aliases=['check_who_require_support', 'cksupreq'])
    @commands.check(if_inside_support_channel)
    async def chksupreq(self, ctx):
        '''Checks who still requires the support.'''
        role_sup = discord.utils.get(ctx.guild.roles, name="SupportRequired")
        l = [m for m in ctx.guild.members if role_sup in m.roles]
        embed = []
        l_no = 0
        if len(l) == 0:
            e = Embed(
                description='Those who still **require support** are **None**! :tada:',
            )
            await ctx.send(embed=e)
            return
        if len(l) > 10:
            for i in range(len(l)//10):
                description = ''
                for l in range(10):
                    try:
                        description += f'\n**({l_no+1}.)** - {l[l_no].mention}'
                        l_no += 1
                    except:
                        pass

                e = Embed(
                    title='Those who still require support:',
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
            for k, i in enumerate(l):
                description += f'\n**({k+1}.)** -  {l[k].mention}'
            e = Embed(
                title='Those who still require support:',
                description=description
            )
            embed.append(e)
            await ctx.send(embed=e)
            return

    @chksupreq.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure) and not isinstance(error, commands.MissingPermissions) and not isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=ErrorEmbed(description='This command can be run **inside only servers\'s support channel**.'))


def setup(bot):
    bot.add_cog(Help(bot))