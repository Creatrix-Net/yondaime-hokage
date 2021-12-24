import asyncio
from collections import Counter, defaultdict

import discord
from discord.ext import commands, tasks


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Some simple moderation commands"
        self._batch_message_lock = asyncio.Lock(loop=bot.loop)
        self.message_batches = defaultdict(list)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="discord_certified_moderator",
                                    id=922030031146995733)

    @tasks.loop(seconds=10.0)
    async def bulk_send_messages(self):
        async with self._batch_message_lock:
            for ((guild_id, channel_id),
                 messages) in self.message_batches.items():
                guild = self.bot.get_guild(guild_id)
                channel = guild and guild.get_channel(channel_id)
                if channel is None:
                    continue

                paginator = commands.Paginator(suffix="", prefix="")
                for message in messages:
                    paginator.add_line(message)

                for page in paginator.pages:
                    try:
                        await channel.send(page)
                    except discord.HTTPException:
                        pass

            self.message_batches.clear()

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.id in (self.bot.user.id, self.bot.owner_id):
            return

        if message.guild is None:
            return

        if not isinstance(author, discord.Member):
            return

        if author.bot:
            return

        # we're going to ignore members with manage messages
        if author.guild_permissions.manage_messages:
            return

        guild_id = message.guild.id
        config = await self.get_guild_config(guild_id)
        if config is None:
            return

        # check for raid mode stuff
        await self.check_raid(config, guild_id, author, message)

        # auto-ban tracking for mention spams begin here
        if len(message.mentions) <= 3:
            return

        if not config.mention_count:
            return

        # check if it meets the thresholds required
        mention_count = sum(not m.bot and m.id != author.id
                            for m in message.mentions)
        if mention_count < config.mention_count:
            return

        if message.channel.id in config.safe_mention_channel_ids:
            return

        try:
            await author.ban(
                reason=f"Spamming mentions ({mention_count} mentions)")
        except Exception as e:
            log.info(
                f"Failed to autoban member {author} (ID: {author.id}) in guild ID {guild_id}"
            )
        else:
            to_send = f"Banned {author} (ID: {author.id}) for spamming {mention_count} mentions."
            async with self._batch_message_lock:
                self.message_batches[(guild_id,
                                      message.channel.id)].append(to_send)

            log.info(
                f"Member {author} (ID: {author.id}) has been autobanned from guild ID {guild_id}"
            )


def setup(bot):
    bot.add_cog(AntiRaid(bot))
