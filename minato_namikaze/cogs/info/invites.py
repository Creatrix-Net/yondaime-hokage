import asyncio
import datetime
import time
from typing import Dict, Optional

import discord
from discord.ext import commands, tasks

# poll period in minutes for the
# update_invite_expiry task
# if you want to change this
# to use seconds you need
# to update the kwarg in the
# decorator too
POLL_PERIOD = 25


class Invites(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._invites_ready = asyncio.Event()
        self._dict_filled = asyncio.Event()

        self.bot.invites = {}
        self.bot.get_invite = self.get_invite
        self.bot.wait_for_invites = self.wait_for_invites

        self.bot.loop.create_task(self.__ainit__())

        self.description = "Get invites information about the server"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{LINK SYMBOL}")

    async def __ainit__(self):
        # wait until the bots internal cache is ready
        await self.bot.wait_until_ready()

        for guild in self.bot.guilds:
            self.bot.invites[guild.id] = await self.fetch_invites(guild) or {}
        self.update_invite_expiry.start()
        self.delete_expired.start()

    def cog_unload(self):
        self.update_invite_expiry.cancel()
        self.delete_expired.cancel()

    @tasks.loop()
    async def delete_expired(self):
        if not self.bot.expiring_invites:
            await self._dict_filled.wait()
        invites = self.bot.expiring_invites
        expiry_time = min(invites.keys())
        inv = invites[expiry_time]
        sleep_time = expiry_time - (int(time.time()) - self.bot.last_update)
        self.bot.shortest_invite = expiry_time
        await asyncio.sleep(sleep_time)
        # delete invite from cache
        self.delete_invite(inv)
        # delete invite from expiring invite list
        # bot.shortest_invite is updated in update_invite_expiry
        # and since the expiring_invites dict is also updated
        # so the time goes down we use this instead
        self.bot.expiring_invites.pop(self.bot.shortest_invite, None)

    @delete_expired.before_loop
    async def wait_for_list(self):
        await self.wait_for_invites()

    @tasks.loop(minutes=POLL_PERIOD)
    async def update_invite_expiry(self):
        # flatten all the invites in the cache into one single list
        flattened = [
            invite for inner in self.bot.invites.values()
            for invite in inner.values()
        ]
        # get current posix time
        current = time.time()
        self.bot.expiring_invites = {
            inv.max_age - int(current - inv.created_at.replace(
                tzinfo=datetime.timezone.utc).timestamp()): inv
            for inv in flattened if inv.max_age != 0
        }

        exists = True

        # update self.bot.shortest_invite
        # so we can compare it with invites
        # that were just created
        try:  # self.bot.shortest_invite might not exist
            self.bot.shortest_invite = self.bot.shortest_invite - int(
                time.time() - self.bot.last_update)
        except AttributeError:
            exists = False

        if self.update_invite_expiry.current_loop == 0:
            # this needs to be updated before
            # setting self._invites_ready
            self.bot.last_update = int(current)
            self._invites_ready.set()
        # we need to check that expiring_invites
        # is truthy otherwise this conditional will
        # raise an error because we passed an
        # empty sequence to min()
        elif (exists and self.bot.expiring_invites and self.bot.shortest_invite
              > min(self.bot.expiring_invites.keys())):
            # this conditional needs to run before we
            # update self._last_update
            self.delete_expired.restart()
            self.bot.last_update = int(current)
        else:
            # the last update needs to be updated regardless or
            # it will cause updates getting deleted from the cache
            # too early because the expiring_invites list will be
            # updated with new times but delete_expired will think
            # that the last update was ages ago and will deduct a huge
            # amount of seconds from the expiry time to form the sleep_time
            self.bot.last_update = int(current)
        # set the event so if the delete_expired
        # task is cancelled it will start again
        if self.bot.expiring_invites:
            self._dict_filled.set()
            self._dict_filled.clear()

    def delete_invite(self, invite: discord.Invite) -> None:
        entry_found = self.get_invites(invite.guild.id)
        entry_found.pop(invite.code, None)

    def get_invite(self, code: str) -> Optional[discord.Invite]:
        for invites in self.bot.invites.values():
            find = invites.get(code)

            if find:
                return find
        return None

    def get_invites(self,
                    guild_id: int) -> Optional[Dict[str, discord.Invite]]:
        return self.bot.invites.get(guild_id, None)

    async def wait_for_invites(self) -> None:
        if not self._invites_ready.is_set():
            await self._invites_ready.wait()

    async def fetch_invites(
            self, guild: discord.Guild) -> Optional[Dict[str, discord.Invite]]:
        try:
            invites = await guild.invites()
        except discord.HTTPException:
            return None
        else:
            return {invite.code: invite for invite in invites}

    async def _schedule_deletion(self, guild: discord.Guild) -> None:
        seconds_passed = 0

        while seconds_passed < 300:
            seconds_passed += 1

            if guild in self.bot.guilds:
                return
            await asyncio.sleep(1)

        if guild not in self.bot.guilds:
            self.bot.invites.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        cached = self.bot.invites.get(invite.guild.id, None)

        if cached:
            cached[invite.code] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        self.delete_invite(invite)

    @commands.Cog.listener()
    async def on_guild_channel_delete(
            self, channel: discord.abc.GuildChannel) -> None:
        invites = self.bot.invites.get(channel.guild.id)

        if invites:
            for invite in list(invites.values()):
                # changed to use id because of doc warning
                if invite.channel.id == channel.id:
                    invites.pop(invite.code)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        invites = await self.fetch_invites(guild) or {}
        self.bot.invites[guild.id] = invites

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild) -> None:
        # reload all invites in case they changed during
        # the time that the guilds were unavailable
        self.bot.invites[guild.id] = await self.fetch_invites(guild) or {}

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.bot.loop.create_task(self._schedule_deletion(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        invites = await self.fetch_invites(member.guild)

        if invites:
            # we sort the invites to ensure we are comparing
            # A.uses == A.uses
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.bot.invites[member.guild.id].values(),
                            key=lambda i: i.code)

            # zipping is the easiest way to compare each in order, and
            # they should be the same size? if we do it properly
            for old, new in zip(cached, invites):
                if old.uses < new.uses:
                    self.bot.invites[member.guild.id][old.code] = new
                    self.bot.dispatch("invite_update", member, new)
                    break

    # if you want to use this command you
    # might want to make a error handler
    # to handle commands.NoPrivateMessage
    @commands.guild_only()
    @commands.command()
    async def invitestats(self, ctx):
        """Displays the top 10 most used invites in the guild."""
        # PEP8 + same code, more readability
        invites = self.bot.invites.get(ctx.guild.id, None)

        # falsey check for None or {}
        if not invites:
            # if there is no invites send this information
            # in an embed and return
            embed = discord.Embed(colour=discord.Colour.red(),
                                  description="No invites found...")
            await ctx.send(embed=embed)
            return

        # if you got here there are invites in the cache
        embed = discord.Embed(colour=discord.Colour.green(),
                              title="Most used invites")
        # sort the invites by the amount of uses
        # by default this would make it in increasing
        # order so we pass True to the reverse kwarg
        invites = sorted(invites.values(), key=lambda i: i.uses, reverse=True)
        # if there are 10 or more invites in the cache we will
        # display 10 invites, otherwise display the amount
        # of invites
        amount = 10 if len(invites) >= 10 else len(invites)
        # list comp on the sorted invites and then
        # join it into one string with str.join
        description = "\n".join([
            f"{i + 1}. {invites[i].code} - {invites[i].uses}"
            for i in range(amount)
        ])
        embed.description = description
        # if there are more than 10 invites
        # add a footer saying how many more
        # invites there are
        if amount > 10:
            embed.set_footer(
                text=f"There are {len(invites) - 10} more invites in this guild.")
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Invites(bot))
