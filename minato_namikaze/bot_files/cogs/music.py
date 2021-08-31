import discord
import DiscordUtils
from discord.ext import commands

from ..lib import Embed, ErrorEmbed


class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""
    pass


class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""
    pass


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = DiscordUtils.Music()
        self.description = 'Listen to some soothing music!'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='🎵')

    async def cog_before_invoke(self, ctx: commands.Context):
        """
        Coroutine called before command invocation.
        We mainly just want to check whether the user is in the players controller channel.
        """
        if ctx.command.name in ('join', 'leave'):
            return
        voice_state_author = ctx.author.voice
        voice_state_me = ctx.me.voice

        if voice_state_author is not None:
            if ctx.command.name == 'play':
                if voice_state_me is None:
                    await ctx.author.voice.channel.connect()
            else:
                if voice_state_author is None:
                    raise NoChannelProvided
        else:
            raise NoChannelProvided

        return

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send(embed=ErrorEmbed(description='You must be in a voice channel or provide one to connect to.'))

    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send(embed=ErrorEmbed(description='Music commands are not available in Private Messages.'))
            return False

        return True

    def songembed(self, song):
        e = Embed()
        e.set_thumbnail(url=song.thumbnail)
        e.set_image(url=song.thumbnail)
        e.title = song.title
        e.add_field(name=f'**{song.channel}**',
                    value=f'[Click Here]({song.channel_url})')
        e.add_field(name=f'**{song.name}**', value=f'[Click Here]({song.url})')
        return e

    @commands.command()
    async def join(self, ctx):
        '''Joins the voice channel'''
        try:
            voice_state_author = ctx.author.voice
            voice_state_me = ctx.me.voice
            if voice_state_author and voice_state_me and voice_state_author == voice_state_me:
                return

            if voice_state_author is None:
                raise NoChannelProvided

            await ctx.author.voice.channel.connect()  # Joins author's voice channel
            await ctx.send('```Joined```')
        except:
            pass

    @commands.command()
    async def leave(self, ctx):
        '''Disconnects from a voice channel'''
        voice_state_me = ctx.me.voice

        if voice_state_me is None:
            return

        try:
            await ctx.send('```Left```')
            await ctx.voice_client.disconnect()
        except:
            pass

    @commands.command(usage='<music.url>')
    async def play(self, ctx, *, url):
        '''Plays Music'''
        e = Embed()
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = self.bot.music.create_player(
                ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            await player.queue(url, search=True)
            song = await player.play()
            e.set_thumbnail(url=song.thumbnail)
            e.title = 'Playing - '+song.title
            e.add_field(name=f'**{song.channel}**',
                        value=f'[Click Here]({song.channel_url})')
            e.add_field(name=f'**{song.name}**',
                        value=f'[Click Here]({song.url})')
            e.set_image(url=song.thumbnail)
        else:
            song = await player.queue(url, search=True)
            e.set_thumbnail(url=song.thumbnail)
            e.title = 'Queued - '+song.title
            e.add_field(name=f'**{song.channel}**',
                        value=f'[Click Here]({song.channel_url})')
            e.add_field(name=f'**{song.name}**',
                        value=f'[Click Here]({song.url})')
            e.set_image(url=song.thumbnail)
        await ctx.send(embed=e)

    @commands.command()
    async def pause(self, ctx):
        '''Pauses the current music playing'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.pause()
        await ctx.send(f"```Paused {song.name}```")

    @commands.command()
    async def resume(self, ctx):
        '''Resumes music'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.resume()
        await ctx.send(f"```Resumed {song.name}```")

    @commands.command()
    async def stop(self, ctx):
        '''Stops the Music Player'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        await ctx.send("```Stopped```")

    @commands.command()
    async def loop(self, ctx):
        '''Iterates the current playing song'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        if song.is_looping:
            await ctx.send(f"```Enabled loop for {song.name}```")
        else:
            await ctx.send(f"```Disabled loop for {song.name}```")

    @commands.command()
    async def queue(self, ctx):
        '''Displays the songs queue'''
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx)
        paginator.add_reaction('⏮️', "first")
        paginator.add_reaction('⏪', "back")
        paginator.add_reaction('🔐', "lock")
        paginator.add_reaction('⏩', "next")
        paginator.add_reaction('⏭️', "last")
        embeds = [self.songembed(song) for song in player.current_queue()]
        await paginator.run(embeds)

    @commands.command()
    async def np(self, ctx):
        '''Gives info about cirrently playing song'''
        e = discord.Embed(color=discord.Color.random())
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        e.set_thumbnail(url=song.thumbnail)
        e.title = 'Playing - '+song.title
        e.add_field(name=f'**{song.channel}**',
                    value=f'[Click Here]({song.channel_url})')
        e.add_field(name=f'**{song.name}**', value=f'[Click Here]({song.url})')
        e.set_image(url=song.thumbnail)
        await ctx.send(embed=e)

    @commands.command()
    async def skip(self, ctx):
        '''Skips the current song'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        if len(data) == 2:
            await ctx.send(f"```Skipped from {data[0].name} to {data[1].name}```")
        else:
            await ctx.send(f"```Skipped {data[0].name}```")

    @commands.command(usage='<value between 1-100>')
    async def volume(self, ctx, vol):
        '''Changes the volume for the current song'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        # volume should be a float between 0 to 1
        song, volume = await player.change_volume(float(vol) / 100)
        await ctx.send(f"Changed volume for {song.name} to {volume*100}%")

    @commands.command(usage='<song.index.value>')
    async def remove(self, ctx, index):
        '''Song the specified song using its index value'''
        player = self.bot.music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f"```Removed {song.name} from queue```")


def setup(bot):
    bot.add_cog(Music(bot))
