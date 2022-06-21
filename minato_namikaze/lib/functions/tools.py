import ast
import copy
import datetime
import os
import pathlib
from typing import AnyStr, Literal, Optional, Union

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
    ctx: commands.Context, *, author=None, channel=None, **kwargs
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
        voice_state_author.channel, discord.VoiceChannel
    ):
        return False
    return True


def check_if_user_joined_a_stage(ctx):
    """Checks is a user joined a stage channel"""
    voice_state_author = ctx.author.voice
    if voice_state_author is None or isinstance(
        voice_state_author.channel, discord.StageChannel
    ):
        return False
    return True


async def get_welcome_channel(
    guild: discord.Guild, bot: discord.Client, inviter_or_guild_owner: discord.User
):
    try:
        return guild.system_channel
    except:
        try:
            text_channels_list = guild.text_channels
            for i in text_channels_list:
                if i.permissions_for(bot.user).send_messages:
                    return i
        except:
            return inviter_or_guild_owner


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


def secure_delete(path: Union[AnyStr, pathlib.Path], passes: int = 3) -> None:
    """
    At first it write the file with some random data , even repeatedly, then delete it
    Meaning the entire contents of the file were still intact and every pass just added to the overall size of the file. So it ended up being [Original Contents][Random Data of that Size][Random Data of that Size][Random Data of that Size] which is not the desired effect obviously
    Firstopen the file in append to find the length,
    then reopen in r+ so that it can seek to the beginning
    (in append mode it seems like what caused the undesired effect is that it was not actually possible to seek to 0)

    Answer was copied from stackoverflow with some type hinting changes :)
    https://stackoverflow.com/questions/17455300/python-securely-remove-file
    """
    with open(path, "ba+", buffering=0) as delfile: # skipcq: PTC-W6004
        length: int = delfile.tell()
    delfile.close()
    with open(path, "br+", buffering=0) as delfile:
        for i in range(passes):
            delfile.seek(0, 0)
            delfile.write(os.urandom(length))
        delfile.seek(0)
        for x in range(length):
            delfile.write(b"\x00")
    os.remove(path)


# R.Danny Code
def format_dt(
    dt, style: Optional[str] = None, ist: Optional[Union[bool, Literal[False]]] = False
):
    if dt.tzinfo is None and not ist:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    if ist:
        timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        dt = dt.replace(tzinfo=timezone)

    if style is None:
        return f"<t:{int(dt.timestamp())}>"
    return f"<t:{int(dt.timestamp())}:{style}>"
