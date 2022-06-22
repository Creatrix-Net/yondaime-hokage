# from https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/reminder.py

from __future__ import annotations

import asyncio
import datetime
import textwrap
from typing import TYPE_CHECKING, Any, Optional

import discord
from discord.ext import commands
from minato_namikaze.lib import (
    plural,
    session,
    human_timedelta,
    format_relative,
    Base,
    FriendlyTimeResult,
    UserFriendlyTime,
    Timer,
    session_obj
)
from sqlalchemy import Column, DateTime, Integer, String, select, delete, insert, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from typing_extensions import Annotated

if TYPE_CHECKING:
    from minato_namikaze.lib import Context
    from .. import MinatoNamikazeBot

import logging

log = logging.getLogger(__name__)


class Reminders(Base):
    __tablename__ = "reminders"

    id = Column(Integer, index=True, primary_key=True)
    expires = Column(DateTime, index=True)
    created = Column(DateTime, default="now() at time zone 'utc'", nullable=False)
    event = Column(String, nullable=False)
    extra = Column(JSONB, nullable=True)


class Reminder(commands.Cog):
    """Reminders to do something."""

    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self._have_data = asyncio.Event(loop=bot.loop)
        self._current_timer: Optional[Timer] = None
        self._task = bot.loop.create_task(self.dispatch_timers())

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{ALARM CLOCK}")

    def cog_unload(self) -> None:
        self._task.cancel()

    async def cog_command_error(self, ctx: "Context", error: commands.CommandError):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))
        if isinstance(error, commands.TooManyArguments):
            await ctx.send(
                f"You called the {ctx.command.name} command with too many arguments."
            )

    async def get_active_timer(
        self, *, days: int = 7
    ) -> Optional[Timer]:
        query = select(Reminders).where(Reminders.expires<datetime.timedelta(days=days))
        async with session_obj() as session:
            try:
                record = (await session.execute(query)).one()
            except (NoResultFound, MultipleResultsFound):
                record = False
        return Timer(record=record) if record else None

    async def wait_for_active_timers(self, *, days: int = 7) -> Timer:
        timer = await self.get_active_timer(days=days)
        if timer is not None:
            self._have_data.set()
            return timer

        self._have_data.clear()
        self._current_timer = None
        await self._have_data.wait()

        # At this point we always have data
        return await self.get_active_timer(days=days)  # type: ignore

    async def call_timer(self, timer: Timer) -> None:
        # delete the timer
        async with session_obj() as session:
            query = delete(Reminders).where(Reminders.id == timer.id)
            await session.execute(query)
            await session.commit()

        # dispatch the event
        event_name = f"{timer.event}_timer_complete"
        self.bot.dispatch(event_name, timer)

    async def dispatch_timers(self) -> None:
        try:
            while not self.bot.is_closed():
                # can only asyncio.sleep for up to ~48 days reliably
                # so we're gonna cap it off at 40 days
                # see: http://bugs.python.org/issue20493
                timer = self._current_timer = await self.wait_for_active_timers(days=40)
                now = datetime.datetime.utcnow()

                if timer.expires >= now:
                    to_sleep = (timer.expires - now).total_seconds()
                    await asyncio.sleep(to_sleep)

                await self.call_timer(timer)
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed):
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_timers())

    async def short_timer_optimisation(self, seconds: int, timer: Timer) -> None:
        await asyncio.sleep(seconds)
        event_name = f"{timer.event}_timer_complete"
        self.bot.dispatch(event_name, timer)

    async def create_timer(self, *args: Any, **kwargs: Any) -> Timer:
        r"""Creates a timer.

        Parameters
        -----------
        when: datetime.datetime
            When the timer should fire.
        event: str
            The name of the event to trigger.
            Will transform to 'on_{event}_timer_complete'.
        \*args
            Arguments to pass to the event
        \*\*kwargs
            Keyword arguments to pass to the event
        created: datetime.datetime
            Special keyword-only argument to use as the creation time.
            Should make the timedeltas a bit more consistent.

        Note
        ------
        Arguments and keyword arguments must be JSON serialisable.

        Returns
        --------
        :class:`Timer`
        """
        when, event, *args = args  # type: ignore

        try:
            now = kwargs.pop("created")
        except KeyError:
            now = discord.utils.utcnow()

        # Remove timezone information since the database does not deal with it
        when = when.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        now = now.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        timer = Timer.temporary(
            event=event, args=args, kwargs=kwargs, expires=when, created=now
        )
        delta = (when - now).total_seconds()
        if delta <= 60:
            # a shortcut for small timers
            self.bot.loop.create_task(self.short_timer_optimisation(delta, timer))
            return timer

        async with session_obj() as session:
            query = insert(Reminders).values(event=event, extra={"args": args, "kwargs": kwargs}, expires=when, created=now).returning(Reminders.id)
            result = await session.execute(query)
            row=result.fetchone()
            await session.commit()

        timer.id = row.id

        # only set the data check if it can be waited on
        if delta <= (86400 * 40):  # 40 days
            self._have_data.set()

        # check if this timer is earlier than our currently run timer
        if self._current_timer and when < self._current_timer.expires:
            # cancel the task and re-run it
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_timers())

        return timer

    @commands.group(
        aliases=["timer", "remind"], usage="<when>", invoke_without_command=True
    )
    async def reminder(
        self,
        ctx: "Context",
        *,
        when: Annotated[
            FriendlyTimeResult,
            UserFriendlyTime(commands.clean_content, default="…"),
        ],
    ):
        """Reminds you of something after a certain amount of time.

        The input can be any direct date (e.g. YYYY-MM-DD) or a human
        readable offset. Examples:

        - "next thursday at 3pm do something funny"
        - "do the dishes tomorrow"
        - "in 3 days do the thing"
        - "2d unmute someone"

        Times are in UTC.
        """

        timer = await self.create_timer(
            when.dt,
            "reminder",
            ctx.author.id,
            ctx.channel.id,
            when.arg,
            created=ctx.message.created_at,
            message_id=ctx.message.id,
        )
        delta = human_timedelta(when.dt, source=timer.created_at)
        await ctx.send(f"Alright {ctx.author.mention}, in {delta}: {when.arg}")

    @reminder.command(name="list", ignore_extra=False)
    async def reminder_list(self, ctx: "Context"):
        """Shows the 10 latest currently running reminders."""
        # query = """SELECT id, expires, extra #>> '{args,2}'
        #            FROM reminders
        #            WHERE event = 'reminder'
        #            AND extra #>> '{args,0}' = $1
        #            ORDER BY expires
        #            LIMIT 10;
        #         """
        query = select(
            Reminders.id, 
            Reminders.expires, 
            Reminders.extra['args'].as_string()
        ).where(and_(Reminders.event == "reminder", Reminders.extra['args'].as_string() == str('ctx.author.id'))).order_by(Reminders.expires).limit(10)

        async with session_obj() as session:
            result = await session.execute(query)
            records=result.all()
            await session.commit()

        if len(records) == 0:
            return await ctx.send("No currently running reminders.")

        e = discord.Embed(colour=discord.Colour.blurple(), title="Reminders")

        if len(records) == 10:
            e.set_footer(text="Only showing up to 10 reminders.")
        else:
            e.set_footer(
                text=f'{len(records)} reminder{"s" if len(records) > 1 else ""}'
            )

        for i in records:
            shorten = textwrap.shorten(i.extra, width=512)
            e.add_field(
                name=f"{i.id}: {format_relative(i.expires)}",
                value=shorten,
                inline=False,
            )

        await ctx.send(embed=e)

    @reminder.command(name="delete", aliases=["remove", "cancel"], ignore_extra=False)
    async def reminder_delete(self, ctx: "Context", *, id: int):
        """Deletes a reminder by its ID.

        To get a reminder ID, use the reminder list command.

        You must own the reminder to delete it, obviously.
        """

        # query = """DELETE FROM reminders
        #            WHERE id=$1
        #            AND event = 'reminder'
        #            AND extra #>> '{args,0}' = $2;
        #         """

        query = select(
            Reminders.id, 
            Reminders.expires, 
            Reminders.extra['args'].as_string()
        ).where(and_(Reminders.event == "reminder", Reminders.extra['args'].as_string() == str('ctx.author.id'))).order_by(Reminders.expires).limit(10)

        async with session_obj() as session:
            result = await session.execute(query)
            records=result.all()
            await session.commit()

        status = await ctx.db.execute(query, id, str(ctx.author.id))
        if status == "DELETE 0":
            return await ctx.send("Could not delete any reminders with that ID.")

        # if the current timer is being deleted
        if self._current_timer and self._current_timer.id == id:
            # cancel the task and re-run it
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_timers())

        await ctx.send("Successfully deleted reminder.")

    @reminder.command(name="clear", ignore_extra=False)
    async def reminder_clear(self, ctx: "Context"):
        """Clears all reminders you have set."""

        # For UX purposes this has to be two queries.

        query = """SELECT COUNT(*)
                   FROM reminders
                   WHERE event = 'reminder'
                   AND extra #>> '{args,0}' = $1;
                """

        author_id = str(ctx.author.id)
        total = await ctx.db.fetchrow(query, author_id)
        total = total[0]
        if total == 0:
            return await ctx.send("You do not have any reminders to delete.")

        confirm = await ctx.prompt(
            f"Are you sure you want to delete {plural(total):reminder}?"
        )
        if not confirm:
            return await ctx.send("Aborting")

        query = """DELETE FROM reminders WHERE event = 'reminder' AND extra #>> '{args,0}' = $1;"""
        await ctx.db.execute(query, author_id)

        # Check if the current timer is the one being cleared and cancel it if so
        if self._current_timer and self._current_timer.author_id == ctx.author.id:
            self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_timers())

        await ctx.send(f"Successfully deleted {plural(total):reminder}.")

    @commands.Cog.listener()
    async def on_reminder_timer_complete(self, timer: Timer):
        author_id, channel_id, message = timer.args

        try:
            channel = self.bot.get_channel(channel_id) or (
                await self.bot.fetch_channel(channel_id)
            )
        except discord.HTTPException:
            return

        guild_id = (
            channel.guild.id
            if isinstance(channel, (discord.TextChannel, discord.Thread))
            else "@me"
        )
        message_id = timer.kwargs.get("message_id")
        msg = f"<@{author_id}>, {timer.human_delta}: {message}"
        view = discord.utils.MISSING

        if message_id:
            url = f"https://discord.com/channels/{guild_id}/{channel.id}/{message_id}"
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Go to original message", url=url))

        try:
            await channel.send(msg, view=view)  # type: ignore
        except discord.HTTPException:
            return


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Reminder(bot))
