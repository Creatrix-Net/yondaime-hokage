import random
from datetime import datetime
from os.path import join

import discord
from discord.ext import commands

from ...lib import BASE_DIR, ChannelAndMessageId, Embed, ErrorEmbed, PostStats


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.minato_gif = bot.minato_gif
        self._cache = bot._cache
        self.posting = PostStats(self.bot)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter_or_guild_owner = await self.bot.get_bot_inviter(guild)
        welcome_channel = await self.bot.get_welcome_channel(
            guild, inviter_or_guild_owner)
        try:
            img = random.choice(self.minato_gif)
            file = discord.File(join(self.BOT.minato_gif, img), filename=img)

            f = open(
                BASE_DIR / join("lib", "text", "welcome_message.txt"),
                "r",
            )

            f1 = f.read()
            description = f1.format(
                guild.name,
                self.bot.user.mention,
                self.bot.user.mention,
                self.bot.user.mention,
                inviter_or_guild_owner.mention,
            )
            e = Embed(
                title="Thanks for Inviting me !",
                description=description,
                timestamp=datetime.utcnow(),
            )
            e.set_author(name=self.bot.user, icon_url=self.bot.user.avatar.url)
            e.set_thumbnail(url=self.bot.user.avatar.url)
            e.set_image(url=f"attachment://{img}")
            await welcome_channel.send(file=file, embed=e)
        except:
            pass

        # Send it to server count channel the support server
        try:
            e34 = discord.Embed(title=f"{guild.name}",
                                color=discord.Color.green(),
                                description="Added")
            if guild.icon:
                e34.set_thumbnail(url=guild.icon.url)
            if guild.banner:
                e34.set_image(url=guild.banner.with_format("png").url)
            c = (self.bot.get_channel(
                ChannelAndMessageId.serverlog_channel2.value)
                if not self.bot.local else self.bot.get_channel(
                ChannelAndMessageId.serverlog_channel1.value))
            e34.add_field(name="**Total Members**", value=guild.member_count)
            e34.add_field(name="**Bots**",
                          value=sum(1 for member in guild.members
                                    if member.bot))
            e34.add_field(name="**Region**",
                          value=str(guild.region).capitalize(),
                          inline=True)
            e34.add_field(name="**Server ID**", value=guild.id, inline=True)
            await c.send(
                content=f"We are now currently at **{len(self.bot.guilds)+1} servers**",
                embed=e34,
            )
        except:
            pass
        await self.posting.post_guild_stats_all()

    # when bot leaves the server
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            e34 = ErrorEmbed(title=f"{guild.name}", description="Left")
            if guild.icon:
                e34.set_thumbnail(url=guild.icon.url)
            if guild.banner:
                e34.set_image(url=guild.banner.with_format("png").url)
            c = (self.bot.get_channel(
                ChannelAndMessageId.serverlog_channel2.value)
                if not self.bot.local else self.bot.get_channel(
                ChannelAndMessageId.serverlog_channel1.value))
            e34.add_field(name="**Total Members**", value=guild.member_count)
            e34.add_field(name="**Bots**",
                          value=sum(1 for member in guild.members
                                    if member.bot))
            e34.add_field(name="**Region**",
                          value=str(guild.region).capitalize(),
                          inline=True)
            e34.add_field(name="**Server ID**", value=guild.id, inline=True)
            await c.send(
                content=f"We are now currently at **{len(self.bot.guilds)+1} servers**",
                embed=e34,
            )
        except:
            pass
        await self.posting.post_guild_stats_all()

    # ban
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        ban = self.bot.return_ban_channel(guild=guild)
        event = False
        try:
            event = await guild.audit_logs().find(
                lambda x: x.action is discord.AuditLogAction.ban)
        except:
            event = False
        if ban:
            e = ErrorEmbed(
                title="**Ban**",
                description=f"**{user.mention}** was banned!",
            )
            e.add_field(name="**Banned User** :", value=user, inline=True)
            if event:
                e.add_field(name="**Responsible Moderator** :",
                            value=event.user,
                            inline=True)
                if event.reason:
                    e.add_field(name="**Reason** :", value=event.reason)
            if user.avatar.url:
                e.set_thumbnail(url=user.avatar.url)
            await ban.send(embed=e)
            try:
                await user.send(f"You were **banned** from **{guild.name}**",
                                embed=e)
            except:
                pass

    # unban
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        unban = self.bot.return_unban_channel(guild=guild)
        event = False
        try:
            event = await guild.audit_logs().find(
                lambda x: x.action is discord.AuditLogAction.unban)
        except:
            event = False
        if unban:
            e = Embed(
                title="**Unban** :tada:",
                description=f"**{user.mention}** was unbanned! :tada:",
            )
            if user.avatar.url:
                e.set_thumbnail(url=user.avatar.url)
            e.add_field(name="**Unbanned User** :", value=user, inline=True)
            if event:
                e.add_field(name="**Responsible Moderator** :",
                            value=event.user,
                            inline=True)
                if event.reason:
                    e.add_field(name="**Reason** :", value=event.reason)
            await unban.send(embed=e)
            try:
                await user.send(
                    f"You were **unbanned** from **{guild.name}** ! :tada:",
                    embed=e)
            except:
                pass

    # on message event
    @commands.Cog.listener()
    async def on_message(self, message):
        if (self.bot.user.mentioned_in(message)
                and message.mention_everyone is False
                and message.content.lower() in
            (f"<@!{self.bot.application_id}>", f"<@{self.bot.application_id}>")
                or message.content.lower() in (
                    f"<@!{self.bot.application_id}> prefix",
                    f"<@{self.bot.application_id}> prefix",
        )) and not message.author.bot:
            await message.channel.send(
                "The prefix is **)** ,A full list of all commands is available by typing ```)help```"
            )

        if message.channel.id in (
                ChannelAndMessageId.error_logs_channel.value,
                ChannelAndMessageId.traceback_channel.value,
        ):
            try:
                await message.publish()
            except:
                pass


def setup(bot):
    bot.add_cog(BotEvents(bot))
