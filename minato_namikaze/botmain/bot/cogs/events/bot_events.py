import random
from asyncio import sleep
from datetime import datetime
from os.path import join
from pathlib import Path

import discord
import DiscordUtils
from discord.ext import commands

from ...lib import (
    Embed,
    ErrorEmbed,
    PostStats,
    get_bot_inviter,
    get_welcome_channel,
    return_ban_channel,
    return_unban_channel,
)


class InviteTrackerForMyGuild:
    def __init__(self, bot):
        self._cache = bot._cache
        self.bot = bot

    async def fetch_inviter_for_my_guild(self, member):
        await sleep(self.bot.latency)
        for new_invite in await member.guild.invites():
            for cached_invite in self._cache[member.guild.id].values():
                if new_invite.code == cached_invite.code and new_invite.uses - cached_invite.uses == 1 or cached_invite.revoked:
                    if cached_invite.revoked:
                        self._cache[member.guild.id].pop(cached_invite.code)
                    elif new_invite.inviter == cached_invite.inviter:
                        self._cache[member.guild.id][cached_invite.code] = new_invite
                    else:
                        self._cache[member.guild.id][cached_invite.code].uses += 1
                    return cached_invite


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.minato_gif = bot.minato_gif
        self.minato_dir = bot.minato_dir
        self.posting = PostStats(self.bot)
        self.tracker = InviteTrackerForMyGuild(bot)   

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 747480356625711204:
            inviter = await self.tracker.fetch_inviter_for_my_guild(member)
            channel = discord.utils.get(
                self.bot.get_all_channels(), id=747660913116577903)
            if not member.bot:
                embed = Embed(
                    title=f"Welcome {member.name} !",
                    description=f"Please {member.mention} goto <#777189846862266408> and get **supercool roles**",
                    timestamp=datetime.utcnow(),
                )
                embed.set_image(url='https://i.imgur.com/mktY446.jpeg')
                embed.set_thumbnail(url='https://i.imgur.com/SizgkEZ.png')
                embed.set_author(name=self.bot.user.name,
                                 icon_url=self.bot.user.avatar_url)
                embed.set_footer(text=f"Welcome {member.name}")

                e = Embed(
                    description=f'**{member}** was invited by **{inviter.inviter}** \n- **INVITE CODE: {inviter.code}**,\n- USES **{inviter.uses} uses**.')
                await channel.send(member.mention, embed=embed)
                await channel.send(embed=e)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        try:
            if invite.guild.id not in self._cache.keys() and invite.guild.id == 747480356625711204:
                self.bot._cache[invite.guild.id] = {}
            self.bot._cache[invite.guild.id][invite.code] = invite
        except:
            pass

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.id not in self._cache.keys():
            return
        ref_invite = self._cache[invite.guild.id][invite.code]
        if (ref_invite.created_at.timestamp()+ref_invite.max_age > datetime.utcnow().timestamp() or ref_invite.max_age == 0) and ref_invite.max_uses > 0 and ref_invite.uses == ref_invite.max_uses-1:
            try:
                async for entry in invite.guild.audit_logs(limit=1, action=AuditLogAction.invite_delete):
                    if entry.target.code != invite.code:
                        self._cache[invite.guild.id][ref_invite.code].revoked = True
                        return
                else:
                    self._cache[invite.guild.id][ref_invite.code].revoked = True
                    return
            except Forbidden:
                self._cache[invite.guild.id][ref_invite.code].revoked = True
                return
        else:
            self._cache[invite.guild.id].pop(invite.code)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter_or_guild_owner = await get_bot_inviter(guild, self.bot)
        welcome_channel = await get_welcome_channel(guild, self.bot, inviter_or_guild_owner)
        try:
            img = random.choice(self.minato_gif)
            file = discord.File(
                join(self.minato_dir, 'minato', img), filename=img)
            
            f = open(Path(__file__).resolve(
                strict=True).parent.parent.parent / join('lib', 'text', 'welcome_message.txt'), 'r')

            f1 = f.read()
            description = f1.format(
                guild.name,
                self.bot.user.mention,
                self.bot.user.mention,
                self.bot.user.mention,
                inviter_or_guild_owner.mention
            )
            e = Embed(
                title='Thanks for Inviting me <:smilenaruto:848961696047300649>',
                description=description,
                timestamp=datetime.utcnow()
            )
            e.set_author(
                name=self.bot.user,
                icon_url=self.bot.user.avatar_url
            )
            e.set_thumbnail(
                url=self.bot.user.avatar_url
            )
            e.set_image(
                url=f"attachment://{img}"
            )
            await welcome_channel.send(content='https://i.imgur.com/j6j7ob7.mp4', file=file, embed=e)
        except:
            pass

        # Send it to server count channel the support server
        try:
            e34 = discord.Embed(title=f'{guild.name}',
                                color=discord.Color.green(), description='Added')
            if guild.icon:
                e34.set_thumbnail(url=guild.icon_url)
            if guild.banner:
                e34.set_image(url=guild.banner_url_as(format="png"))
            c = self.bot.get_channel(
                813954921782706227) if not self.bot.local else self.bot.get_channel(869238107524968479)
            e34.add_field(name='**Total Members**', value=guild.member_count)
            e34.add_field(name='**Bots**',
                          value=sum(1 for member in guild.members if member.bot))
            e34.add_field(name="**Region**",
                          value=str(guild.region).capitalize(), inline=True)
            e34.add_field(name="**Server ID**", value=guild.id, inline=True)
            await c.send(content=f'We are now currently at **{len(self.bot.guilds)+1} servers**',embed=e34)
        except:
            pass
        await self.posting.post_guild_stats_all()

    # when bot leaves the server
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            e34 = ErrorEmbed(title=f'{guild.name}', description='Left')
            if guild.icon:
                e34.set_thumbnail(url=guild.icon_url)
            if guild.banner:
                e34.set_image(url=guild.banner_url_as(format="png"))
            c = self.bot.get_channel(
                813954921782706227) if not self.bot.local else self.bot.get_channel(869238107524968479)
            e34.add_field(name='**Total Members**', value=guild.member_count)
            e34.add_field(name='**Bots**',
                          value=sum(1 for member in guild.members if member.bot))
            e34.add_field(name="**Region**",
                          value=str(guild.region).capitalize(), inline=True)
            e34.add_field(name="**Server ID**", value=guild.id, inline=True)
            await c.send(content=f'We are now currently at **{len(self.bot.guilds)+1} servers**',embed=e34)
        except:
            pass
        await self.posting.post_guild_stats_all()

    # ban
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ban = return_ban_channel(guild=guild)
        event = False
        try:
            event = await guild.audit_logs().find(lambda x: x.action is discord.AuditLogAction.ban)
        except:
            event = False
        if ban:
            e = ErrorEmbed(
                title='**Ban**',
                description=f'**{user.mention}** was banned!',
            )
            e.add_field(name='**Banned User** :', value=user, inline=True)
            if event:
                e.add_field(name='**Responsible Moderator** :',
                            value=event.user, inline=True)
                if event.reason:
                    e.add_field(name='**Reason** :', value=event.reason)
            if user.avatar_url:
                e.set_thumbnail(url=user.avatar_url)
            await ban.send(embed=e)
            try:
                await user.send(f'You were **banned** from **{guild.name}**', embed=e)
            except:
                pass

    # unban
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        unban = return_unban_channel(guild=guild)
        event = False
        try:
            event = await guild.audit_logs().find(lambda x: x.action is discord.AuditLogAction.unban)
        except:
            event = False
        if unban:
            e = Embed(
                title='**Unban** :tada:',
                description=f'**{user.mention}** was unbanned! :tada:'
            )
            if user.avatar_url:
                e.set_thumbnail(url=user.avatar_url)
            e.add_field(name='**Unbanned User** :', value=user, inline=True)
            if event:
                e.add_field(name='**Responsible Moderator** :',
                            value=event.user, inline=True)
                if event.reason:
                    e.add_field(name='**Reason** :', value=event.reason)
            await unban.send(embed=e)
            try:
                await user.send(f'You were **unbanned** from **{guild.name}** ! :tada:', embed=e)
            except:
                pass

    # on message event
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message) and message.mention_everyone is False and message.content.lower() in ('<@!779559821162315787>', '<@779559821162315787>') or message.content.lower() in ('<@!779559821162315787> prefix', '<@779559821162315787> prefix'):
            if not message.author.bot:
                await message.channel.send('The prefix is **)** ,A full list of all commands is available by typing ```)help```')


def setup(bot):
    bot.add_cog(BotEvents(bot))
