import asyncio
import time
from os.path import join

import discord
from discord.ext import commands

from ..lib import *


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Setups up the server for feedback, ban and unban logs and also setups the channel and roles to create a support management system for the server.'
        self.file = discord.File(
            join(self.bot.minato_dir, 'discord', 'pin.png'), filename='pin.png')
        self.embed = Embed(description='Please **check** the **channel pins**')

    @commands.command(name='setup', description="Easy setup for the server")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def _setup(self, ctx):
        'A command that setups up the server for feedback, ban and unban logs and also setups the channel and roles to create a support management system for the server.'
        await ctx.message.delete()
        commanwaitingtime = 60.0
        waitingtime_bet_mesg = 3.0

        self.embed.set_image(url="attachment://pin.png")

        admin_roles, overwrite_dict = perms_dict(ctx)
        feed_channel, support_channel, support_channel_roles, ban, unban, warns, botask = await channel_creation(
            ctx)

        if feed_channel and support_channel and ban and unban and warns:
            e = Embed(
                title='You have already configured your server mate!',
                description=f'Please head over to {feed_channel.mention} {support_channel.mention} {ban.mention} {unban.mention} {warns.mention}'
            )

            if not support_channel and support_channel_roles:
                await ctx.guild.create_role(name="SupportRequired")

            await feed_channel.send(file=self.file, embed=self.embed)
            time.sleep(1)
            await support_channel.send(file=self.file, embed=self.embed)
            time.sleep(1)
            await ban.send(file=self.file, embed=self.embed)
            time.sleep(1)
            await unban.send(file=self.file, embed=self.embed)
            time.sleep(1)
            await warns.send(file=self.file, embed=self.embed)
            time.sleep(1)
            await ctx.send(embed=e)

        else:
            # Bot Setup Channel
            if not botask:
                botask = await ctx.guild.create_text_channel("Bot Setup", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
                await ctx.send(f'**{botask.mention}** channel is **created** please head over there for the server setup of the bot!', delete_after=8)
                await ctx.send(f'Roles having access to {botask.mention} are', delete_after=8)
                for i in admin_roles:
                    await ctx.send(f'{i.mention}', delete_after=10)
            else:
                await ctx.send(f'Please head over the {botask.mention}', delete_after=10)

            # Feedback
            if not feed_channel:
                m = Feedback(bot=self.bot, timeout=commanwaitingtime)
                await m.start(ctx, channel=botask)
                await asyncio.sleep(waitingtime_bet_mesg)
            else:
                await ctx.send(f'The channel for logging of feedback is already there {feed_channel.mention}', delete_after=5)
                await feed_channel.send(file=self.file, embed=self.embed)

            # Support
            if not support_channel:
                m = Support(bot=self.bot, timeout=commanwaitingtime)
                await m.start(ctx, channel=botask)
                await asyncio.sleep(waitingtime_bet_mesg)
            else:
                await ctx.send(f'The channel for support is already there {support_channel.mention}', delete_after=5)
                await support_channel.send(file=self.file, embed=self.embed)

            # Ban
            if not ban:
                m = Ban(bot=self.bot, timeout=commanwaitingtime)
                await m.start(ctx, channel=botask)
                await asyncio.sleep(waitingtime_bet_mesg)
            else:
                await ctx.send(f'Channel for **logging bans already there**! {ban.mention}', delete_after=5)

            # UnBan
            if not unban:
                m = Unban(bot=self.bot, timeout=commanwaitingtime)
                await m.start(ctx, channel=botask)
                await asyncio.sleep(waitingtime_bet_mesg)
            else:
                await ctx.send(f'Channel for **logging unbans already there**! {unban.mention}', delete_after=5)

            # Warns
            if not warns:
                m = Warns(bot=self.bot, timeout=commanwaitingtime)
                await m.start(ctx, channel=botask)
                await asyncio.sleep(waitingtime_bet_mesg)
            else:
                await ctx.send(f'Channel for **logging warns already there**! {warns.mention}', delete_after=5)

            # Setup Finish
            await botask.send('**Deleting this setup channel in**')
            gb = await botask.send(30)
            for i in range(1, 30):
                await gb.edit(content=30-i)
                time.sleep(1)
            await botask.delete()


def setup(bot):
    bot.add_cog(ServerSetup(bot))
