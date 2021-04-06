import asyncio

import discord
from discord.ext import commands


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Setups up the server for feedback, ban and unban logs and also setups the channel and roles to create a support management system for the server.'
    
    @commands.command(name='setup',description="Easy setup for the server")
    @commands.has_permissions(administrator=True)
    async def _setup(self,ctx):
        admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator and not role.managed]
        overwrite_dict = {}
        for i in admin_roles:
            overwrite_dict[i] = discord.PermissionOverwrite(read_messages=True)
        overwrite_dict.update({ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),ctx.guild.me: discord.PermissionOverwrite(read_messages=True)})
        
        category = discord.utils.get(ctx.guild.categories, name="Admin / Feedback") if discord.utils.get(ctx.guild.categories, name="Admin / Feedback") else False
        bingo = discord.utils.get(ctx.guild.categories, name="Bingo Book") if discord.utils.get(ctx.guild.categories, name="Bingo Book") else False
        if not category:category = await ctx.guild.create_category("Admin / Feedback", overwrites = overwrite_dict, reason="To log the admin and feedback events")

        #Setup / Feedback
        botask = discord.utils.get(category.channels, name="bot-setup") if discord.utils.get(category.channels, name="bot-setup") else False
        feed_channel = discord.utils.get(category.channels, name="feedback") if discord.utils.get(category.channels, name="feedback") else False

        #Bingo Book
        try: ban = discord.utils.get(bingo.channels, name="ban") if discord.utils.get(bingo.channels, name="ban") else False
        except: ban = False
        
        try: unban = discord.utils.get(bingo.channels, name="unban") if discord.utils.get(bingo.channels, name="unban") else False
        except: unban = False

        #Support
        support_channel = discord.utils.get(category.channels, name="support") if discord.utils.get(category.channels, name="support") else False
        support_channel_roles = discord.utils.get(ctx.guild.roles, name="Support_Required") if discord.utils.get(ctx.guild.roles, name="Support_Required") else False
        
        if feed_channel and support_channel and ban and unban: 
            await ctx.send('You have already configured your server mate!')
            await feed_channel.send('@here This channel will be used to log the feedbacks given by members.')

            sup_roles = support_channel_roles if support_channel_roles else await ctx.guild.create_role(name="Support_Required")
            await support_channel.send('@here This channel will be used as the support channel who needs support!')
            await support_channel.send(f'Once the member uses the support command they will be given a role of {sup_roles.mention} to access this channel')
            await support_channel.send(f'Then you can use resolved command if the issue has been resolved!')
            await ctx.send(f'Please head over to {feed_channel.mention} {support_channel.mention}')

        else:
            reactions = ['\u2705','\u274C','✅','❌']
            right = ['\u2705','✅']
            
            #Bot Setup Channel
            if not botask:
                botask = await ctx.guild.create_text_channel("Bot Setup", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                await ctx.send(f'**{botask.mention}** channel is **created** please head over there for the server setup of the bot!')
                await ctx.send(f'Roles having access to {botask.mention} are')
                for i in admin_roles:
                    await ctx.send(f'{i.mention}')
            else: await ctx.send(f'Please head over the {botask.mention}')
            
            #Feedback
            if not feed_channel:
                embed = discord.Embed(title=f"@here Want to create a feedback system for the **{ctx.guild.name}** ?")
                embed.add_field(name="Yes", value=":white_check_mark:")
                embed.add_field(name="No", value=":x:")
                feedback = await botask.send(embed=embed)
                await feedback.add_reaction('\u2705')
                await feedback.add_reaction('\u274C')
                try:
                    _, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                        and _reaction.message.channel == botask
                        and _reaction.message == feedback and str(_reaction.emoji) in reactions and user != ctx.bot.user
                        and not user.bot,
                        timeout=60,)
                    if str(_.emoji) in right:
                        feed = await ctx.guild.create_text_channel("Feedback", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                        await botask.send(f'{feed.mention} channel **created** for logging the **feedbacks** for the {ctx.guild.name} by members!')
                        await feed.send('@here This channel will be used to log the feedbacks given by members.')
                    else:
                        await botask.send(f'**Okay** no feedback system will be there for the **{ctx.guild.name}**')
                except asyncio.TimeoutError:
                    feed = await ctx.guild.create_text_channel("Feedback", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                    await botask.edit(embed=discord.Embed(description="No reaction from the **Administrators**!! So creating all **Channels and roles as per my requirements!** for the feedback system for the **{ctx.guild.name}**"))
                    await feed.send('@here This channel will be used to log the feedbacks given by members.')
                    await botask.send(f'{feed.mention} channel **created** for logging the **feedbacks** for the {ctx.guild.name} by members!')
            else: 
                await ctx.send(f'The channel for logging of feedback is already there {feed_channel.mention}')
                await feed_channel.send('@here This channel will be used to log the feedbacks given by members.')
            
            #Support
            if not support_channel:
                embed = discord.Embed(title=f"@here Want to create a support system for the **{ctx.guild.name}** ?")
                embed.add_field(name="Yes", value=":white_check_mark:")
                embed.add_field(name="No", value=":x:")
                support = await botask.send(embed=embed)
                await support.add_reaction('\u2705')
                await support.add_reaction('\u274C')
                try:
                    _, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                        and _reaction.message.channel == botask
                        and _reaction.message == support and str(_reaction.emoji) in reactions and user != ctx.bot.user
                        and not user.bot,
                        timeout=60,)
                    if str(_.emoji) in right:
                        sup_roles = await ctx.guild.create_role(name="Support_Required")
                        overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support_Required"): discord.PermissionOverwrite(read_messages=False)})
                        sup = await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                        await botask.send(f'{sup.mention} channel **created** as the **support** channel for the {ctx.guild.name} server!')
                        await sup.send('@here This channel will be used as the support channel who needs support!')
                        await sup.send(f'Once the member uses the support command they will be given a role of {sup_roles.mention} to access this channel')
                        await sup.send(f'Then you can use resolved command if the issue has been resolved!')
                    else:
                        await botask.send(f'**Okay** no support system will be there for the **{ctx.guild.name}**') 
                except asyncio.TimeoutError:
                    sup_roles = await ctx.guild.create_role(name="Support_Required")
                    overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support_Required"): discord.PermissionOverwrite(read_messages=False)})
                    sup = await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                    await botask.edit(embed=discord.Embed(description=f"No reaction from the **Administrators**!! So creating all **Channels and roles as per my requirements!** for the support system for the **{ctx.guild.name}**"))
                    await sup.send('@here This channel will be used as the support channel who needs support!')
                    await sup.send(f'Once the member uses the support command they will be given a role of {sup_roles.mention} to access this channel')
                    await sup.send(f'Then you can use resolved command if the issue has been resolved!')
                    await botask.send(f'{sup.mention} channel **created** as the **support** channel for the {ctx.guild.name} server!')
            else:
                await ctx.send(f'The channel for support is already there {support_channel.mention}')
                sup_roles = support_channel_roles if support_channel_roles else await ctx.guild.create_role(name="Support_Required")
                await support_channel.send('@here This channel will be used as the support channel who needs support!')
                await support_channel.send(f'Once the member uses the support command they will be given a role of {sup_roles.mention} to access this channel')
                await support_channel.send(f'Then you can use resolved command if the issue has been resolved!')
            
            #Ban
            if not ban:
                embed = discord.Embed(title=f"@here Want to log bans for the **{ctx.guild.name}** ?")
                embed.add_field(name="Yes", value=":white_check_mark:")
                embed.add_field(name="No", value=":x:")
                ban1 = await botask.send(embed=embed)
                await ban1.add_reaction('\u2705')
                await ban1.add_reaction('\u274C')
                try:
                    _, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                        and _reaction.message.channel == botask
                        and _reaction.message == ban1 and str(_reaction.emoji) in reactions and user != ctx.bot.user
                        and not user.bot,
                        timeout=60,)
                    if str(_.emoji) in right:
                        if not bingo:bingo = await ctx.guild.create_category("Bingo Book", reason="To log the the bans and unban events")
                        
                        ban = await ctx.guild.create_text_channel("ban", category=discord.utils.get(ctx.guild.categories, name="Bingo Book"))
                        await botask.send(f'{feed.mention} channel **created** for logging the **bans** for the {ctx.guild.name}')
                        await ban.send('@here This channel will be used to log the server ban.')
                    else:
                        await botask.send(f'**Okay** no logging system for the **{ctx.guild.name}** bans will be there') 
                except asyncio.TimeoutError:
                    if not bingo:bingo = await ctx.guild.create_category("Bingo Book", reason="To log the the bans and unban events")
                        
                    ban = await ctx.guild.create_text_channel("ban", category=discord.utils.get(ctx.guild.categories, name="Bingo Book"))
                    await botask.send(f'{ban.mention} channel **created** for logging the **bans** for the {ctx.guild.name}')
                    await ban.send('@here This channel will be used to log the server ban.')

            #UnBan
            if not unban:
                embed = discord.Embed(title=f"@here Want to log unbans for the **{ctx.guild.name}** ?")
                embed.add_field(name="Yes", value=":white_check_mark:")
                embed.add_field(name="No", value=":x:")
                unban1 = await botask.send(embed=embed)
                await unban1.add_reaction('\u2705')
                await unban1.add_reaction('\u274C')
                try:
                    _, user = await ctx.bot.wait_for(
                        "reaction_add",
                        check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                        and _reaction.message.channel == botask
                        and _reaction.message == unban1 and str(_reaction.emoji) in reactions and user != ctx.bot.user
                        and not user.bot,
                        timeout=60,)
                    if str(_.emoji) in right:
                        if not bingo:bingo = await ctx.guild.create_category("Bingo Book", reason="To log the the bans and unban events")
                        
                        unban = await ctx.guild.create_text_channel("unban", category=discord.utils.get(ctx.guild.categories, name="Bingo Book"))
                        await botask.send(f'{unban.mention} channel **created** for logging the **unbans** for the {ctx.guild.name}')
                        await unban.send('@here This channel will be used to log the server unban.')
                    else:
                        await botask.send(f'**Okay** no logging system for the **{ctx.guild.name}** unbans will be there')
                except asyncio.TimeoutError:
                    if not bingo:bingo = await ctx.guild.create_category("Bingo Book", reason="To log the the bans and unban events")
                        
                    unban = await ctx.guild.create_text_channel("unban", category=discord.utils.get(ctx.guild.categories, name="Bingo Book"))
                    await botask.send(f'{unban.mention} channel **created** for logging the **unbans** for the {ctx.guild.name}')
                    await unban.send('@here This channel will be used to log the server unban.')

            #Setup Finish
            import time
            await botask.send('Deleting this setup channel in')
            gb = await botask.send(5)
            for i in range(1,5):
                await gb.edit(content=5-i)
                time.sleep(1)
            await botask.delete()

def setup(bot):
    bot.add_cog(ServerSetup(bot))
