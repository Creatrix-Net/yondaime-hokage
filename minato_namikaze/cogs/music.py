from typing import TYPE_CHECKING, Union

import discord
from discord.ext import commands
from DiscordUtils import (
    Embed,
    EmbedPaginator,
    ErrorEmbed,
    StarboardEmbed,
    SuccessEmbed,
    Music,
)
from lib import IncorrectChannelError, NoChannelProvided

if TYPE_CHECKING:
    from lib import Context
    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.bot.music = Music()
        self.description = "Listen to some soothing music!"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="voice_channel", id=942447961210753047)

    async def cog_before_invoke(self, ctx: "Context"):
        """
        Coroutine called before command invocation.
        We mainly just want to check whether the user is in the players controller channel.
        """
        if ctx.command.name.lower() == "leave":
            return
        voice_state_author = ctx.author.voice
        voice_state_me = ctx.me.voice

        if voice_state_author is not None:
            if ctx.command.name.lower() in ("play", "join"):
                if voice_state_me is None:
                    await ctx.author.voice.channel.connect()
            else:
                if voice_state_author is None:
                    raise NoChannelProvided
        else:
            raise NoChannelProvided
        return

    async def cog_command_error(self, ctx: "Context", error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send(
                embed=ErrorEmbed(
                    description="You must be in a voice channel or provide one to connect to."
                )
            )

    async def cog_check(self, ctx: "Context"):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send(
                embed=ErrorEmbed(
                    description="Music commands are not available in Private Messages."
                )
            )
            return False

        return True

    @staticmethod
    def songembed(song, queued: bool = False):
        e = Embed(
            title=song.title if not queued else f"Queued - {song.title}", url=song.url
        )
        e.set_image(url=song.thumbnail)
        e.description = f"- {song.channel} : {song.channel_url}"
        e.timestamp = discord.utils.utcnow()
        e.set_footer(
            text=f"Views: {song.views} | Duration: {round(song.duration/60)} minutes",
            icon_url=song.thumbnail,
        )
        return e

    @commands.command()
    async def join(self, ctx: "Context"):
        """Joins the voice channel"""
        voice_state_author = ctx.author.voice
        voice_state_me = ctx.me.voice
        if (
            voice_state_author
            and voice_state_me
            and voice_state_author == voice_state_me
        ):
            return

        if voice_state_author is None:
            raise NoChannelProvided

        await ctx.author.voice.channel.connect()  # Joins author's voice channel
        await ctx.send(embed=SuccessEmbed(description="```Joined```"))

    @commands.command()
    async def leave(self, ctx: "Context"):
        """Disconnects from a voice channel"""
        voice_state_me = ctx.me.voice

        if voice_state_me is None:
            return

        try:
            await ctx.send(embed=ErrorEmbed(description="```Left```"))
            await ctx.voice_client.disconnect()
        except:
            pass

    @commands.command(usage="<music.url | music.name>")
    async def play(self, ctx: "Context", *, url):
        """Plays the requested music"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = self.bot.music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            await player.queue(url, search=True)
            song = await player.play()
            await ctx.send(embed=self.songembed(song))
        else:
            song = await player.queue(url, search=True)
            await ctx.send(embed=self.songembed(song, queued=True))

    @commands.command()
    async def pause(self, ctx: "Context"):
        """Pauses the current music playing"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.pause()
        await ctx.send(embed=StarboardEmbed(description=f"```Paused {song.name}```"))

    @commands.command()
    async def resume(self, ctx: "Context"):
        """Resumes music"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.resume()
        await ctx.send(embed=StarboardEmbed(description=f"```Resumed {song.name}```"))

    @commands.command()
    async def stop(self, ctx: "Context"):
        """Stops the Music Player"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        await ctx.send(embed=ErrorEmbed(description="```Stopped```"))

    @commands.command()
    async def loop(self, ctx: "Context"):
        """Iterates the current playing song"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        if song.is_looping:
            await ctx.send(
                embed=SuccessEmbed(description=f"```Enabled loop for {song.name}```")
            )
        else:
            await ctx.send(
                embed=ErrorEmbed(description=f"```Disabled loop for {song.name}```")
            )

    @commands.command()
    async def queue(self, ctx: "Context"):
        """Displays the songs queue"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        paginator = EmbedPaginator(
            ctx=ctx, entries=[self.songembed(song) for song in player.current_queue()]
        )
        await paginator.start()

    @commands.command()
    async def np(self, ctx: "Context"):
        """Gives info about current playing song"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        await ctx.send(embed=self.songembed(song))

    @commands.command()
    async def skip(self, ctx: "Context"):
        """Skips the current playing song"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        if len(data) == 2:
            await ctx.send(
                embed=SuccessEmbed(
                    description=f"```Skipped from {data[0].name} to {data[1].name}```"
                )
            )
        else:
            await ctx.send(
                embed=SuccessEmbed(description=f"```Skipped {data[0].name}```")
            )

    @commands.command(usage="<value between 1-100>", aliases=["vol"])
    async def volume(self, ctx: "Context", vol: Union[int, float]):
        """
        Changes the volume for the current song
        `Note: Negative volume numbers will be converted to 0`
        """
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        vol = abs(vol)
        vol = max(vol, 0)
        if vol > 100:
            return await ctx.send(
                embed=ErrorEmbed(description="The volume should be between 0 and 100")
            )
        # volume should be a float between 0 to 1
        song, volume = await player.change_volume(float(vol / 100))
        await ctx.send(
            embed=SuccessEmbed(
                description=f"Changed volume for **{song.name}** to {volume:.2}%"
            )
        )

    @commands.command(usage="<song.index.value>")
    async def remove_song(self, ctx: "Context", index: int):
        """Song the specified song using its index value"""
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(embed=ErrorEmbed(f"```Removed {song.name} from queue```"))

    @volume.error
    @remove_song.error
    @skip.error
    @np.error
    @queue.error
    @pause.error
    @stop.error
    @resume.error
    @loop.error
    async def error_handler(self, ctx: "Context", error, *args, **kwargs):
        await ctx.send(
            embed=ErrorEmbed(description="No song in the queue"), delete_after=5
        )


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Music(bot))
