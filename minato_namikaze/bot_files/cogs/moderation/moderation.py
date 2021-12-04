import datetime
import re
import shlex
from collections import Counter
from os.path import join
from typing import Optional, Union

import discord
from discord.ext import commands

from ...lib import (
    ActionReason,
    Arguments,
    BannedMember,
    ErrorEmbed,
    MemberID,
    PostStats,
    check_if_warning_system_setup,
    has_permissions,
)


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Some simple moderation commands"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="discord_certified_moderator",
                                    id=876846223926128701)

    # set delay
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def setdelay(self, ctx, seconds: int):
        """Sets Slowmode Of A Channel"""
        current_slow = ctx.channel.slowmode_delay
        if current_slow == seconds:
            return await ctx.send(
                f"Sorry, But this channel already has {seconds} set as the delay! (I don't want to waste my api calls lmao)"
            )
        message = f"Set the slowmode delay in this channel to {seconds} seconds!"
        if seconds == 0:
            message = f"Reset Slowmode of channel {ctx.channel.name}"
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"{message}")

    # kick
    @commands.command(
        name="kick",
        description="A command which kicks a given user",
        usage="<user> [reason]",
    )
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """A command which kicks a given user"""
        await ctx.guild.kick(user=member, reason=reason)

        embed = discord.Embed(title=f"{ctx.author.name} kicked: {member.name}",
                              description=reason)
        await ctx.send(embed=embed)

    # ban
    @commands.command(
        name="ban",
        description="A command which bans a given user",
        usage="<user> [reason]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: Union[MemberID, discord.Member],
        *,
        reason: ActionReason = None,
    ):
        """A command which bans a given user"""
        if member in (ctx.message.author, ctx.message.author.id):
            await ctx.send(embed=ErrorEmbed(
                description="You **can't ban yourself**!"))
            return
        try:
            await ctx.guild.ban(user=member, reason=reason)
        except:
            await ctx.send(
                embed=ErrorEmbed(
                    description="Can't ban the member. Please make sure **my role is at the top**!"
                ),
                delete_after=4,
            )
            return

        embed = ErrorEmbed(title=f"{ctx.author.name} banned: {member.name}",
                           description=reason)
        await ctx.send(embed=embed)

    # banlist
    @commands.command(
        name="banlist",
        description="Shows list of users who have been banned! Or position of a specified user who was banned!",
        usage="Optional[<member.id> or <member.mention> or <member.name.with.tag>]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def banlist(self, ctx, *, member: Optional[Union[str, int,
                                                           discord.Member]]):
        banned_users = list(await ctx.guild.bans())
        if not member:
            if len(banned_users) == 0:
                await ctx.send(embed=discord.Embed(
                    description="There is **no-one banned**! :zero: people are **banned**")
                )
                return
            l_no = 0
            pages = []
            if len(banned_users) > 10:
                for i in range(len(banned_users) // 10):
                    description = ""
                    for l in range(10):
                        try:
                            description += f"\n{l_no+1}. - **{banned_users[l_no].user}** : ID [ **{banned_users[l_no].user.id}** ] "
                            l_no += 1
                        except:
                            pass

                    embed = ErrorEmbed(title="Those who were banned are:",
                                       description=description)
                    pages.append(embed)

                paginator = EmbedPaginator(ctx=ctx, entries=pages)
                await paginator.start()
            else:
                description = ""
                for k, i in enumerate(banned_users):
                    description += f"\n{k+1}. - **{i.user}** : ID [ **{banned_users[k].user.id}** ] "
                embed = ErrorEmbed(title="Those who were banned are:",
                                   description=description)
                pages.append(embed)
                await ctx.send(embed=embed)
                return
        else:
            if member.isdigit():
                member = int(member)
            if isinstance(member, str):
                member_name, member_discriminator = member.split("#")

            n = 0
            for i, ban_entry in enumerate(banned_users):
                user = ban_entry.user
                embed = ErrorEmbed(topic=f"About the ban {member}")
                if isinstance(member, str):
                    if (user.name, user.discriminator) == (
                            member_name,
                            member_discriminator,
                    ):
                        if ban_entry.reason:
                            embed.add_field(name="**Reason**",
                                            value=ban_entry.reason,
                                            inline=True)
                        embed.add_field(name="**Position**",
                                        value=i + 1,
                                        inline=True)
                        embed.add_field(
                            name="**Banned User Name**",
                            value=ban_entry.user,
                            inline=True,
                        )
                        embed.set_thumbnail(url=ban_entry.user.avatar.url)
                        await ctx.channel.send(embed=embed)
                        n += 1
                        return

                elif isinstance(member, int):
                    if user.id == int(member):
                        if ban_entry.reason:
                            embed.add_field(name="**Reason**",
                                            value=ban_entry.reason,
                                            inline=True)
                        embed.add_field(name="**Position**",
                                        value=i + 1,
                                        inline=True)
                        embed.add_field(
                            name="**Banned User Name**",
                            value=ban_entry.user,
                            inline=True,
                        )
                        embed.set_thumbnail(url=ban_entry.user.avatar.url)
                        await ctx.channel.send(embed=embed)
                        n += 1
                        return

                else:
                    if user == member:
                        if ban_entry.reason:
                            embed.add_field(name="**Reason**",
                                            value=ban_entry.reason,
                                            inline=True)
                        embed.add_field(name="**Position**",
                                        value=i + 1,
                                        inline=True)
                        embed.add_field(
                            name="**Banned User Name**",
                            value=ban_entry.user,
                            inline=True,
                        )
                        embed.set_thumbnail(url=ban_entry.user.avatar.url)
                        await ctx.channel.send(embed=embed)
                        n += 1
                        return
            if n == 0:
                await ctx.send(embed=ErrorEmbed(
                    description=f"The **{member}** isn't there in the **ban list**"))
                return

    # Soft Ban
    @commands.command()
    @commands.guild_only()
    @has_permissions(kick_members=True)
    async def softban(self,
                      ctx,
                      member: MemberID,
                      *,
                      reason: ActionReason = None):
        """Soft bans a member from the server.

        A softban is basically banning the member from the server but
        then unbanning the member as well. This allows you to essentially
        kick the member while removing their messages.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must have Kick Members permissions.
        """

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send("\N{OK HAND SIGN}")

    # Unban
    @commands.command()
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def unban(self,
                    ctx,
                    member: BannedMember,
                    *,
                    reason: ActionReason = None):
        """Unbans a member from the server.

        You can pass either the ID of the banned member or the Name#Discrim
        combination of the member. Typically the ID is easiest to use.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must have Ban Members permissions.
        """

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(
                f"Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}."
            )
        else:
            await ctx.send(f"Unbanned {member.user} (ID: {member.user.id}).")

    # Add Roles
    @commands.command(pass_context=True,
                      usage="<member.mention> <role>",
                      alias=["add_roles"])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def ar(
        self,
        ctx,
        member: Optional[Union[int, discord.Member]],
        role: Union[int, discord.Role],
    ):
        """Adds a role to a given user"""
        if member is None:
            member = ctx.message.author
        member = ctx.get_user(member)
        role = ctx.get_roles(role)
        await member.add_roles(role)
        embed = discord.Embed(
            title="Added Roles",
            description=f"I have added the role '{role.mention}' to {member.mention}!",
        )
        await ctx.send(embed=embed)

    # Warn
    @commands.command(pass_context=True,
                      usage="<member.mention> <optional: reason>")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.check(check_if_warning_system_setup)
    async def warn(self,
                   ctx,
                   member: Union[int, discord.Member],
                   *,
                   reason: str = None):
        """Warn a user"""
        member = ctx.get_user(member)
        e = ErrorEmbed(title="You have been warned!")
        e.add_field(
            name="**Responsible Moderator**:",
            value=ctx.message.author.mention,
            inline=True,
        )
        if reason:
            e.add_field(name="**Reason**:", value=reason, inline=True)

        warning_channel = ctx.return_warning_channel(ctx.guild)
        await member.send(embed=e)
        await warning_channel.send(embed=e, content=member.mention)
        await ctx.send(
            f"{member.mention} has been **warned** by you ||{ctx.author.mention}||",
            delete_after=10,
        )

    @warn.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            e = ErrorEmbed(
                title=f"No warning system setup for the {ctx.guild.name}",
                description="You can always setup the **warning system** using `)setup` command",
            )
            await ctx.send(embed=e)

    @commands.command(pass_context=True, usage="<member.mention>")
    @commands.guild_only()
    @commands.check(check_if_warning_system_setup)
    async def warnlist(self,
                       ctx,
                       member: Optional[Union[int, discord.Member]] = None):
        """Get the no. of warns for a specified user"""
        member = ctx.get_user(
            member if member is not None else ctx.message.author)
        embed = discord.Embed(title="Type the below message in the search bar")
        search_image = discord.File(join(self.bot.minato_dir, "discord",
                                         "search.png"),
                                    filename="search.png")
        embed.set_image(url="attachment://search.png")
        await ctx.send(file=search_image, embed=embed)

        warning_channel = self.return_warning_channel(ctx.guild)
        message = f"mentions: {member}  in: {warning_channel}"
        await ctx.send(message)

    @warnlist.error
    async def warnlist_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            e = ErrorEmbed(
                title=f"No warning system setup for the {ctx.guild.name}",
                description="You/Admin can always setup the **warning system** using `)setup` command",
            )
            await ctx.send(embed=e)

    @commands.command(aliases=["newmembers"])
    @commands.guild_only()
    async def newusers(self, ctx, *, count: Optional[int] = 5):
        """
        Tells you the newest members of the server.

        This is useful to check if any suspicious members have
        joined.

        The count parameter clamps the number in between 5 - 25
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            members = await ctx.guild.chunk(cache=True)

        members = sorted(ctx.guild.members,
                         key=lambda m: m.joined_at,
                         reverse=True)[:count]

        embed = discord.Embed(title="New Members",
                              colour=discord.Colour.green())

        for member in members:
            joined = member.joined_at.strftime("%a, %d %B %Y %I:%M:%S %fms %Z")
            created = member.created_at.strftime(
                "%a, %d %B %Y %I:%M:%S %fms %Z")
            body = f"Joined: {joined}\nCreated: {created}"
            embed.add_field(name=f"{member} (ID: {member.id})",
                            value=body,
                            inline=False)

        await ctx.send(embed=embed)

    # RDanny code from here
    async def _basic_cleanup_strategy(self, ctx, search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me and not (msg.mentions
                                             or msg.role_mentions):
                await msg.delete()
                count += 1
        return {"Bot": count}

    async def _complex_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.bot.get_guild_prefixes(
            ctx.guild))  # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search,
                                          check=check,
                                          before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    async def _regular_user_cleanup_strategy(self, ctx, search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))

        def check(m):
            return (m.author == ctx.me or m.content.startswith(prefixes)
                    ) and not (m.mentions or m.role_mentions)

        deleted = await ctx.channel.purge(limit=search,
                                          check=check,
                                          before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    async def cleanup(self, ctx, search=100):
        """Cleans up the bot's messages from the channel.

        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.

        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.

        Members with Manage Messages can search up to 1000 messages.
        Members without can search up to 25 messages.
        """

        strategy = self._basic_cleanup_strategy
        is_mod = ctx.channel.permissions_for(ctx.author).manage_messages
        if ctx.channel.permissions_for(ctx.me).manage_messages:
            if is_mod:
                strategy = self._complex_cleanup_strategy
            else:
                strategy = self._regular_user_cleanup_strategy

        if is_mod:
            search = min(max(2, search), 1000)
        else:
            search = min(max(2, search), 25)

        spammers = await strategy(ctx, search)
        deleted = sum(spammers.values())
        messages = [
            f'{deleted} message{" was" if deleted == 1 else "s were"} removed.'
        ]
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(),
                              key=lambda t: t[1],
                              reverse=True)
            messages.extend(f"- **{author}**: {count}"
                            for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)

    @commands.command(
        name="simeplepurge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, amount=5):
        """A command which purges the channel it is called in"""
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=4)

    @commands.group(aliases=["purge"])
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def remove(self, ctx):
        """
        Removes messages that meet a criteria.

        In order to use this command, you must have Manage Messages permissions.
        Note that the bot needs Manage Messages as well. These commands cannot
        be used in a private message.

        When the command is done doing its work, you will get a message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    async def do_removal(self,
                         ctx,
                         limit,
                         predicate,
                         *,
                         before=None,
                         after=None):
        if limit > 2000:
            return await ctx.send(
                f"Too many messages to search given ({limit}/2000)")

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit,
                                              before=before,
                                              after=after,
                                              check=predicate)
        except discord.Forbidden as e:
            return await ctx.send(
                "I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [
            f'{deleted} message{" was" if deleted == 1 else "s were"} removed.'
        ]
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(),
                              key=lambda t: t[1],
                              reverse=True)
            messages.extend(f"**{name}**: {count}" for name, count in spammers)

        to_send = "\n".join(messages)

        if len(to_send) > 2000:
            await ctx.send(f"Successfully removed {deleted} messages.",
                           delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @remove.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search,
                              lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name="all")
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.

        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send(
                "The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @remove.command(name="bot", aliases=["bots"])
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""
        def predicate(m):
            return (m.webhook_id is None
                    and m.author.bot) or (prefix
                                          and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @remove.command(name="emoji", aliases=["emojis"])
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @remove.command(name="reactions")
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(
                f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if message.reactions:
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")

    @remove.command()
    async def custom(self, ctx, *, args: str):
        """
        A more advanced purge command.

        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.

        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.

        The following options are valid.

        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.

        Flag options (no arguments):

        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument("--user", nargs="+")
        parser.add_argument("--contains", nargs="+")
        parser.add_argument("--starts", nargs="+")
        parser.add_argument("--ends", nargs="+")
        parser.add_argument("--or", action="store_true", dest="_or")
        parser.add_argument("--not", action="store_true", dest="_not")
        parser.add_argument("--emoji", action="store_true")
        parser.add_argument("--bot",
                            action="store_const",
                            const=lambda m: m.author.bot)
        parser.add_argument("--embeds",
                            action="store_const",
                            const=lambda m: len(m.embeds))
        parser.add_argument("--files",
                            action="store_const",
                            const=lambda m: len(m.attachments))
        parser.add_argument("--reactions",
                            action="store_const",
                            const=lambda m: len(m.reactions))
        parser.add_argument("--search", type=int)
        parser.add_argument("--after", type=int)
        parser.add_argument("--before", type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r"<:(\w+):(\d+)>")
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(
                lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(
                lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(
                lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any

        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        if args.after and args.search is None:
            args.search = 2000

        if args.search is None:
            args.search = 100

        args.search = max(0, min(2000, args.search))  # clamp from 0-2000
        await self.do_removal(ctx,
                              args.search,
                              predicate,
                              before=args.before,
                              after=args.after)


def setup(bot):
    bot.add_cog(Moderation(bot))
