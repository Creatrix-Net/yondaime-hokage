import contextlib
import inspect
import io
import json
import os
import subprocess as sp
import logging
import textwrap
import traceback
from contextlib import redirect_stdout
from pathlib import Path

import discord
from discord.ext import commands
from json.decoder import JSONDecodeError
from lib import *

log = logging.getLogger(__name__)


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.posting = PostStats(self.bot)
        self.minato_gif = []
        self.description = "These set of commands are only locked to the developer"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{GEAR}\ufe0f")

    def owners(ctx):
        return ctx.author.id == ctx.bot.owner_id

    async def _send_guilds(self, ctx, guilds, title):
        if len(guilds) == 0:
            await ctx.send(embed=ErrorEmbed(
                description="No such guild was found."))
            return

        all_pages = []

        for chunk in [guilds[i:i + 20] for i in range(0, len(guilds), 20)]:
            page = Embed(title=title)

            for guild in chunk:
                if page.description == discord.Embed.Empty:
                    page.description = guild
                else:
                    page.description += f"\n{guild}"

            page.set_footer(text="Use the buttons to flip pages.")
            all_pages.append(page)

        if len(all_pages) == 1:
            embed = all_pages[0]
            embed.set_footer(text=discord.Embed.Empty)
            await ctx.send(embed=embed)
            return

        paginator = EmbedPaginator(entries=all_pages, ctx=ctx)
        await paginator.start()

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.check(owners)
    async def dev(self, ctx, command=None):
        """These set of commands are only locked to the developer"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return
    
    @dev.command()
    async def cleanup_data(self, ctx):
        '''Cleans the uncessary data from the database'''
        #Reaction Roles
        database = await self.bot.db.new(database_category_name,reaction_roles_channel_name)
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(lambda a: str(a), list(data.keys())))
                try:
                    await commands.MessageConverter().convert(ctx,int(data_keys[0]))
                except commands.CommandError:
                    await database.delete(data_keys[0])
            except JSONDecodeError:
                await message.delete()
                continue
        await ctx.send('Reaction Roles :ok_hand:', delete_after=4)
        
        #Setup Vars
        database = await self.bot.db.new(database_category_name,database_channel_name)
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(lambda a: str(a), list(data.keys())))
                try:
                    await commands.GuildConverter().convert(ctx,int(data_keys[0]))
                except commands.CommandError:
                    await database.delete(data_keys[0])
            except JSONDecodeError:
                await message.delete()
                continue
        await ctx.send('Setup Vars :ok_hand:', delete_after=4)

        #Antiraid
        database = await self.bot.db.new(database_category_name,antiraid_channel_name)
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(lambda a: str(a), list(data.keys())))
                try:
                    await commands.GuildConverter().convert(ctx,int(data_keys[0]))
                except commands.CommandError:
                    await database.delete(data_keys[0])
            except JSONDecodeError:
                await message.delete()
                continue
        await ctx.send('AntiRaid :ok_hand:', delete_after=4)

        #Mention Spam
        database = await self.bot.db.new(database_category_name,mentionspam_channel_name)
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(lambda a: str(a), list(data.keys())))
                try:
                    await commands.GuildConverter().convert(ctx,int(data_keys[0]))
                except commands.CommandError:
                    await database.delete(data_keys[0])
            except JSONDecodeError:
                await message.delete()
                continue
        await ctx.send('MentionSpam :ok_hand:', delete_after=4)

        #Backup
        async for message in self.bot.get_channel(ChannelAndMessageId.backup_channel.value).history(limit=None):
            cnt = message.content
            try:
                if int(cnt) not in list(map(lambda a: a.id, self.bot.guilds)):
                    await message.delete()
            except JSONDecodeError:
                await message.delete()
        await ctx.send('Backups :ok_hand:', delete_after=4)
        await ctx.message.delete()

    @dev.command(name="sharedservers", usage="<user>")
    async def sharedservers(self, ctx, *, user: Union[discord.Member, MemberID]):
        """Get a list of servers the bot shares with the user."""
        guilds = [
            f"{guild.name} `{guild.id}` ({guild.member_count} members)"
            for guild in list(user.mutual_guilds)
        ]

        await self._send_guilds(ctx, guilds, "Shared Servers")

    @dev.command(usage="<server ID>")
    async def createinvite(self, ctx, *, guild: commands.GuildConverter):
        """Create an invite to the specified server"""
        try:
            try:
                invite = (await guild.invites())[0]
            except:
                try:
                    invite = (await guild.text_channels())[0].create_invite(
                        max_age=120)
                except:
                    await ctx.send(embed=ErrorEmbed(
                        description="No permissions to create an invite link.")
                    )
                    return

            await ctx.send(embed=Embed(
                description=f"Here is the invite link: {invite.url}"))
        except Exception as e:
            log.error(e)
            await ctx.send(embed=ErrorEmbed(description="Sorry! This is not possible for this server!"))

    @dev.command(invoke_without_command=True, name="eval")
    async def _eval(self, ctx, *, body):
        """Evaluates python code"""
        env = {
            "self": self,
            "ctx": ctx,
            "bot": self.bot,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "source": inspect.getsource,
            "owner": self.bot.get_user(ctx.guild.owner_id),
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith("```") and content.endswith("```"):
                return "\n".join(content.split("\n")[1:-1])

            # remove `foo`
            return content.strip("` \n")

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            """Simple generator that paginates text."""
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text) - 1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != "", pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")
            return await ctx.message.add_reaction("\u2049")

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```"
                                 )
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await ctx.send(f"```py\n{value}\n```")
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f"```py\n{page}\n```")
                                break
                            await ctx.send(f"```py\n{page}\n```")
            else:
                try:
                    out = await ctx.send(f"```py\n{value}{ret}\n```")
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f"```py\n{page}\n```")
                            break
                        await ctx.send(f"```py\n{page}\n```")

        if out:
            await ctx.message.add_reaction("\u2705")  # tick
        elif err:
            await ctx.message.add_reaction("\u2049")  # x
        else:
            await ctx.message.add_reaction("\u2705")

    @dev.command(invoke_without_command=True)
    async def sync(self, ctx):
        """Sync with GitHub and reload all the cogs"""
        embed = Embed(title="Syncing...",
                      description=":joy: Syncing and reloading cogs.")
        embed.set_footer(text=f"{ctx.author} | Minato Namikaze")
        msg = await ctx.send(embed=embed)
        async with ctx.channel.typing():
            output = sp.getoutput("git pull")
        embed = Embed(
            title="Synced",
            description="Synced with GitHub and reloaded all the cogs.")
        # Reload Cogs as well
        cog_dir = Path(__file__).resolve(strict=True).parent.parent
        error_collection = []
        for file in os.listdir(cog_dir):
            if os.path.isdir(cog_dir / file):
                for i in os.listdir(cog_dir / file):
                    if i.endswith(".py"):
                        try:
                            self.bot.reload_extension(
                                f"cogs.{file.strip(' ')}.{i[:-3]}")
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")
            else:
                if file.endswith(".py"):
                    try:
                        self.bot.reload_extension(f"cogs.{file[:-3]}")
                    except Exception as e:
                        return await ctx.send(f"```py\n{e}```")

        if error_collection:
            err = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{err}")

        await msg.edit(embed=embed)

    @dev.command(name="pretend")
    async def pretend(self, ctx: commands.Context, target: Union[discord.User, MemberID], *, command_string: str):
        """Execute my commands pretending as others | usage: <member.mention> <command.name> eg: )own as @Minato angel"""
        if ctx.guild:
            # Try to upgrade to a Member instance
            # This used to be done by a Union converter, but doing it like this makes
            #  the command more compatible with chaining, e.g. `jsk in .. jsk su ..`
            target_member = None

            with contextlib.suppress(discord.HTTPException):
                target_member = ctx.guild.get_member(
                    target.id) or await ctx.guild.fetch_member(target.id)

            target = target_member or target

        alt_ctx = await copy_context_with(ctx,
                                          author=target,
                                          content=ctx.prefix + command_string)

        if alt_ctx.command is None:
            if alt_ctx.invoked_with is None:
                return await ctx.send(
                    "This bot has been hard-configured to ignore this user.")
            return await ctx.send(
                f'Command "{alt_ctx.invoked_with}" is not found')

        return await alt_ctx.command.invoke(alt_ctx)

    @dev.command()
    async def get_commands_in_json(self, ctx):
        """
        Give you all commands details in a json format
        """
        json_to_be_given = {}
        for name in self.bot.cogs:
            cog_commands_list = []
            for command in self.bot.cogs[name].get_commands():
                if not command.hidden:
                    command_dict = {
                        "name": command.name,
                        "short_doc": command.short_doc,
                    }
                    if command.usage:
                        command_dict.update({"usage": command.usage})
                    if command.aliases:
                        command_dict.update({"aliases": command.aliases})
                    if command.description:
                        command_dict.update(
                            {"description": command.description})
                    if command.clean_params or len(command.params) != 0:
                        command_dict.update(
                            {"params": [i for i in command.clean_params]})
                    cog_commands_list.append(command_dict)
            if len(cog_commands_list) != 0 :
                json_to_be_given.update({name: {'cog_commands_list':cog_commands_list, 'description': self.bot.cogs[name].description}})
        with open(BASE_DIR / os.path.join('lib','data','commands.json'),'w') as f:
            json.dump(json_to_be_given,f)
        try:
            await ctx.message.delete()
        except discord.Forbidden or discord.HTTPException:
            pass
        await ctx.send(":ok_hand:")

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def changestat(self, ctx):
        """Change the bot status"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @changestat.command(invoke_without_command=True)
    async def stream(self, ctx, *, activity="placeholder (owner to lazy lol)"):
        """Streaming Activity"""
        await self.bot.change_presence(activity=discord.Streaming(
            status=discord.Status.idle,
            name=activity,
            url="https://www.twitch.tv/dhruvacube",
        ))
        await ctx.send(
            f"```diff\n- Changed activity to {activity} using Stream status.```"
        )

    @changestat.command(invoke_without_command=True)
    async def game(self, ctx, *, activity="placeholder (owner to lazy lol)"):
        """Game Activity"""
        await self.bot.change_presence(status=discord.Status.idle,
                                       activity=discord.Game(name=activity))
        await ctx.send(
            f"```md\n# Changed activity to {activity} using Game status.```")

    @changestat.command(invoke_without_command=True)
    async def watching(self,
                       ctx,
                       *,
                       activity="placeholder (owner to lazy lol)"):
        """Watching activity"""
        await self.bot.change_presence(activity=discord.Activity(
            status=discord.Status.idle,
            type=discord.ActivityType.watching,
            name=activity,
        ))
        await ctx.send(
            f"```arm\nChanged activity to {activity} using Watching status.```"
        )

    @changestat.command(invoke_without_command=True)
    async def listening(self,
                        ctx,
                        *,
                        activity="placeholder (owner to lazy lol)"):
        """Listenting Activity"""
        await self.bot.change_presence(activity=discord.Activity(
            status=discord.Status.idle,
            type=discord.ActivityType.listening,
            name=activity,
        ))
        await ctx.send(
            f"```fix\nChanged activity to {activity} using Listening status.```"
        )

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
                if self.bot.local else self.bot.get_channel(
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

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        inviter_or_guild_owner = await self.bot.get_bot_inviter(guild)
        welcome_channel = await self.bot.get_welcome_channel(
            guild, inviter_or_guild_owner)
        try:
            img = random.choice(minato_gif)
            file = discord.File(img[-1], filename=img[0])

            f = open(
                BASE_DIR / join("lib", "data", "welcome_message.txt"),
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
                timestamp=discord.utils.utcnow(),
            )
            e.set_author(name=self.bot.user, icon_url=self.bot.user.avatar.url)
            e.set_thumbnail(url=self.bot.user.avatar.url)
            e.set_image(url=f"attachment://{img[0]}")
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
                if self.bot.local else self.bot.get_channel(
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


def setup(bot):
    bot.add_cog(Developer(bot))
