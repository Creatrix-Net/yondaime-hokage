from __future__ import annotations

import ast
import copy
import datetime
from typing import AnyStr
from typing import Literal
from typing import Optional
from typing import Union

import discord
from discord.ext import commands


def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


async def copy_context_with(
    ctx: commands.Context,
    *,
    author=None,
    channel=None,
    **kwargs,
):

    alt_message: discord.Message = copy.copy(ctx.message)
    alt_message._update(kwargs)  # pylint: disable=protected-access

    if author is not None:
        alt_message.author = author
    if channel is not None:
        alt_message.channel = channel

    # obtain and return a context of the same type
    return await ctx.bot.get_context(alt_message, cls=type(ctx))


def check_if_user_joined_a_voice(ctx):
    """Checks is a user joined a voice channel"""
    voice_state_author = ctx.author.voice
    if voice_state_author is None or isinstance(
        voice_state_author.channel,
        discord.VoiceChannel,
    ):
        return False
    return True


def check_if_user_joined_a_stage(ctx):
    """Checks is a user joined a stage channel"""
    voice_state_author = ctx.author.voice
    if voice_state_author is None or isinstance(
        voice_state_author.channel,
        discord.StageChannel,
    ):
        return False
    return True


# R.Danny Code
class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


# R.Danny Code
def human_join(seq, delim=", ", final="or"):
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


# R.Danny Code
def format_dt(
    dt,
    style: str | None = None,
    ist: bool | Literal[False] | None = False,
):
    if dt.tzinfo is None and not ist:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    if ist:
        timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        dt = dt.replace(tzinfo=timezone)

    if style is None:
        return f"<t:{int(dt.timestamp())}>"
    return f"<t:{int(dt.timestamp())}:{style}>"
