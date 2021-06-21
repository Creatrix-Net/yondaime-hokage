from typing import Optional, Union

from ...lib import Embed, check_if_support_is_setup, get_user

import discord
from discord.ext import commands
import DiscordUtils


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Displays the support command for the server, this can onnly be used if the server owner has enabled it.'

    @commands.command(description='Open support ticket if enabled by the server admins')
    @commands.cooldown(1, 120, commands.BucketType.guild)
    @commands.guild_only()
    async def support(self, ctx):
        '''Open support ticket if enabled by the server admins'''
        chan = discord.utils.get(
                ctx.guild.channels, 
                topic='This channel will be used as a support channel for this server.',
            )
        if not chan:
            chan = False
        
        if chan:
            if ctx.message.author == ctx.guild.owner:
                await ctx.send(f'{ctx.message.author.mention} really you need support ??! **LOL !** :rofl:')
            
            elif discord.utils.get(ctx.guild.roles, name="SupportRequired") in ctx.message.author.roles:
                await ctx.send(f'{ctx.author.mention} you already applied for the support , please check the {chan.mention} channel.')
            
            else:
                channel = ctx.channel
                await ctx.message.author.add_roles(discord.utils.get(ctx.guild.roles, name="SupportRequired"))
                if channel.guild is ctx.guild:
                    per = ctx.author.mention
                    e = Embed(
                        title='Help Required',
                        description = f"{per} in {channel.mention} needs support!"
                    )
                    await chan.send("@here",embed=e)
                    await ctx.send(f"**Help Desk** has been has been notifed!")
                    e = Embed(
                        title='Support Requirement Registered',
                        description = f'Your need for the support in **{ctx.guild.name}** has been registered'
                    )
                    await ctx.message.author.send('Hello',embed=e)
                else:
                    pass
        else:
            await ctx.send(f'**Sorry to say** {ctx.author.mention}, but **no support channel** has been setup for the {ctx.guild.name} by the admin! **So, I can\'t help you**')
    
    
    @commands.command(description='Resolves the existing ticket!',usage='<member.mention>')
    @commands.check(check_if_support_is_setup)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def resolved(self, ctx, member: Optional[Union[int, discord.Member]]):
        '''Resolves the existing ticket!'''
        member = get_user(member)
        if not discord.utils.get(ctx.guild.roles, name="SupportRequired") in member.roles:
            e = Embed(
                title = 'Sorry !',
                description = f'{member.mention} has not requested any **support** !'
            )
            await ctx.send(embed=e)
            return
        await member.send(f'Hope your issue has been resolved in {ctx.guild.name}, {member.mention}')
        await ctx.send(f'The issue/query for {member.mention} has been set to resolved!')
        await member.remove_roles(discord.utils.get(ctx.guild.roles, name="SupportRequired"))
    
    @commands.command(description='Resolves the existing ticket!')
    async def chksupreq(ctx):
        role_sup = discord.utils.get(ctx.guild.roles, name="SupportRequired")
        l = [m for m in ctx.guild.members if role_sup in m.roles]
        embed = []
        l_no = 0
        for i in range(len(l//10)):
            description = ''
            for l in range(10):
                description += f'\n**{l_no+1}** {l[l_no].mention}'
                l_no += 1
            
            e = Embed(
                title = 'Those who still require support',
                description = description
            )
            embed.append(e)
        
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        
        await paginator.run(embed)

def setup(bot):
    bot.add_cog(Help(bot))
