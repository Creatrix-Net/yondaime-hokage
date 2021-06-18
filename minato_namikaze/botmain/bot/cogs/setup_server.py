import asyncio

import discord
from discord.ext import commands
from os.path import join

from ..lib.classes.setup import *
from ..lib.classes import *
from ..lib.util.setup_server import *
import time


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Setups up the server for feedback, ban and unban logs and also setups the channel and roles to create a support management system for the server.'
        self.file = discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png')
        self.embed = Embed(description='Please **check** the **channel pins**')
    
    @commands.command(name='setup',description="Easy setup for the server")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def _setup(self,ctx):
        'A command that setups up the server for feedback, ban and unban logs and also setups the channel and roles to create a support management system for the server.'
        await ctx.message.delete()
        
        self.embed.set_image(url="attachment://pin.png")
        
        admin_roles, overwrite_dict = perms_dict(ctx)
        feed_channel,support_channel,support_channel_roles,ban,unban,botask = channel_creation(ctx)
        
        if feed_channel and support_channel and ban and unban: 
            e = Embed(
                title ='You have already configured your server mate!',
                description = f'Please head over to {feed_channel.mention} {support_channel.mention} {ban.mention} {unban.mention}'
            )
            
            await feed_channel.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            time.sleep(1)
            sup_roles = support_channel_roles if support_channel_roles else await ctx.guild.create_role(name="SupportRequired")
            await support_channel.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            time.sleep(1)
            await ban.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            time.sleep(1)
            await unban.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            time.sleep(1)
            await ctx.send(embed=e)

        else:
            reactions = ['\u2705','\u274C','✅','❌']
            right = ['\u2705','✅']
            
            #Bot Setup Channel
            if not botask:
                botask = await ctx.guild.create_text_channel("Bot Setup", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                await ctx.send(f'**{botask.mention}** channel is **created** please head over there for the server setup of the bot!', delete_after=8)
                await ctx.send(f'Roles having access to {botask.mention} are', delete_after=8)
                for i in admin_roles:
                    await ctx.send(f'{i.mention}', delete_after=10)
            else: await ctx.send(f'Please head over the {botask.mention}', delete_after=10)
            
            #Feedback
            if not feed_channel:
                m = Feedback()
                await m.start(ctx,channel=botask)
            else: 
                await ctx.send(f'The channel for logging of feedback is already there {feed_channel.mention}', delete_after=5)
                await feed_channel.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            
            #Support
            if not support_channel:
                embed = discord.Embed(title=f"Want to create a support system for the **{ctx.guild.name}** ?")
                embed.add_field(name="Yes", value=":white_check_mark:")
                embed.add_field(name="No", value=":x:")
                support = await botask.send(embed=embed)
                await support.add_reaction('\u2705')
                await support.add_reaction('\u274C')
                n=0
                while True:
                    try:
                        _, user = await ctx.bot.wait_for(
                            "reaction_add",
                            check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                            and _reaction.message.channel == botask
                            and _reaction.message == support and str(_reaction.emoji) in reactions and user != ctx.bot.user
                            and not user.bot,
                            timeout=60,)
                        if str(_.emoji) in right:
                            sup_roles = await ctx.guild.create_role(name="SupportRequired")
                            overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support_Required"): discord.PermissionOverwrite(read_messages=False)})
                            sup = await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                            await botask.send(f'{sup.mention} channel **created** as the **support** channel for the {ctx.guild.name} server!')
                            a=await sup.send('@here **This channel** will be used as the **support channel** who needs support!')
                            b=await sup.send(f'Once the member uses the **`)support` command** they will be given a role of **{sup_roles.mention}** to **access this channel**')
                            c=await sup.send(f'Then you can use **`)resolved`** command if the **issue has been resolved!**')
                            await a.pin()
                            await b.pin()
                            await c.pin()
                            n+=1
                        else:
                            n+=1
                            await botask.send(f'**Okay** no support system will be there for the **{ctx.guild.name}**') 
                    except asyncio.TimeoutError:
                        n+=1
                        sup_roles = await ctx.guild.create_role(name="Support_Required")
                        overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support_Required"): discord.PermissionOverwrite(read_messages=False)})
                        sup = await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                        await botask.edit(embed=discord.Embed(description=f"No reaction from the **Administrators**!! So creating all **Channels and roles as per my requirements!** for the support system for the **{ctx.guild.name}**"))
                        a=await sup.send('@here **This channel** will be used as the **support channel** who needs support!')
                        b=await sup.send(f'Once the member uses the **`)support` command** they will be given a role of **{sup_roles.mention}** to **access this channel**')
                        c=await sup.send(f'Then you can use **`)resolved`** command if the **issue has been resolved!**')
                        await a.pin()
                        await b.pin()
                        await c.pin()
                        await botask.send(f'{sup.mention} channel **created** as the **support** channel for the {ctx.guild.name} server!')
                    except:
                        await botask.send('Invalid reaction given, please choose from ✅ or ❌', delete_after=4)
                    if n>0: break
            else:
                await ctx.send(f'The channel for support is already there {support_channel.mention}', delete_after=5)
                sup_roles = support_channel_roles if support_channel_roles else await ctx.guild.create_role(name="Support_Required")
                await support_channel.send(file=discord.File(join(self.bot.minato_dir, 'pin.png'), filename='pin.png'),embed=self.embed)
            
            #Ban
            if not ban:
                m = Ban()
                await m.start(ctx,channel=botask)
            else:
                await ctx.send(f'Channels for **logging bans already there**! {ban.mention}', delete_after=5)

            #UnBan
            if not unban:
                m = Unban()
                await m.start(ctx,channel=botask)
            else:
                await ctx.send(f'Channels for **logging unbans already there**! {unban.mention}', delete_after=5)

            #Setup Finish
            await botask.send('Deleting this setup channel in')
            gb = await botask.send(5)
            for i in range(1,5):
                await gb.edit(content=5-i)
                time.sleep(1)
            await botask.delete()

def setup(bot):
    bot.add_cog(ServerSetup(bot)) 
