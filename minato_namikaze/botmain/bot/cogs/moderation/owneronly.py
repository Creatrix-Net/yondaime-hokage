import asyncio
import contextlib
import datetime
import io
import typing
from datetime import datetime

import aiohttp
import discord
from discord.ext import commands

from ...lib import copy_context_with


class OwnerOnly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.appleapiisbad = True
        self.description = 'Some commands which is only restricted to server owners.'

    def owners(ctx):
        return ctx.author.id == ctx.guild.owner_id

    @commands.group(invoke_without_command=True, description = 'Type )help own and to get list of all commands under own group')
    @commands.guild_only()
    async def own(self, ctx, command=None):
        '''Type )help own and to get list of all commands under own group'''
        command2 = self.bot.get_command(f"{command}")
        if command2 is None:
            await ctx.send_help(ctx.command)
        else:
            if command is None:
                await ctx.send_help(ctx.command)
            else:
                
                pass

    @own.group(aliases=["ss"])
    async def screenshot(self, ctx, url):
        '''Take a screenshot of a site'''
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        embed = discord.Embed(title=f"Screenshot of {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{url}') as r:
                res = await r.read()
            embed.set_image(url="attachment://ss.png")
            embed.set_footer(
                text=f"{ctx.author} | Minato Namikaze | {current_time} ")
            await ctx.send(file=discord.File(io.BytesIO(res), filename="ss.png"), embed=embed)
            

    @own.group()
    async def leaveguildbecauseimmad(self, ctx):
        '''Make bot leave the guild ! Lol !'''
        message2 = ctx.message
        owner = self.bot.get_user(ctx.guild.owner_id)
        await message2.add_reaction('\U00002705')
        await ctx.send("um, my owners mad so im leaving lmao")
        await asyncio.sleep(2)
        msg = await ctx.send("bomb going of in : 5")
        await asyncio.sleep(1)
        await msg.edit(content="4")
        await asyncio.sleep(1)
        await msg.edit(content="3")
        await asyncio.sleep(1)
        await msg.edit(content="I'm bored now, good bye suckers lmao")
        
        await owner.send("Finally. You have escaped level one")


    @commands.is_owner()
    @own.group(name="as", usage='')
    async def foddd(self, ctx: commands.Context, target: discord.User, *, command_string: str):
        '''Execute my commands pretending as others | usage: <member.mention> <command.name> eg: )own as @Minato angel'''
        if ctx.guild:
            # Try to upgrade to a Member instance
            # This used to be done by a Union converter, but doing it like this makes
            #  the command more compatible with chaining, e.g. `jsk in .. jsk su ..`
            target_member = None

            with contextlib.suppress(discord.HTTPException):
                target_member = ctx.guild.get_member(target.id) or await ctx.guild.fetch_member(target.id)

            target = target_member or target

        alt_ctx = await copy_context_with(ctx, author=target, content=ctx.prefix + command_string)

        if alt_ctx.command is None:
            if alt_ctx.invoked_with is None:
                return await ctx.send('This bot has been hard-configured to ignore this user.')
            return await ctx.send(f'Command "{alt_ctx.invoked_with}" is not found')

        return await alt_ctx.command.invoke(alt_ctx)

    @own.group(invoke_without_command=True)
    @commands.check(owners)
    async def chnick(self, ctx, *, name):
        '''Changes the nickname of someone'''
        me3 = ctx.guild.me
        await me3.edit(nick=name)
        word1 = "Nickname Changed To"
        await ctx.send(f"{word1} {name}")

    @commands.command(usage='<channel id> or <channel.mention starting with #> <message to send>')
    @commands.has_permissions(manage_guild=True)
    async def send(self, ctx, id: typing.Optional[int] = None, channel: discord.TextChannel = None,*, message):
        '''Sends your message/announcement to specific channel'''
        if id is None and channel is None:
            id = message
            channel2 = ctx.channel
            await channel2.send(f"{id}")
            await ctx.author.send(f"Sent your message in {channel2} :)")
        elif id is None and channel is not None:
            await channel.send(f"{message}")
            await ctx.author.send(f"Sent your message in {channel} :)")
        else:
            channel1 = self.bot.get_channel(int(id))
            await channel1.send(f"{message}")
            await ctx.author.send(f"Sent your message in {channel} :)")


def setup(bot):
    bot.add_cog(OwnerOnly(bot))
