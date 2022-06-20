import datetime
import io
import re
import shlex
from collections import Counter
from os.path import join
from typing import TYPE_CHECKING, Optional, Union

import discord
from discord.ext import commands
from minato_namikaze.lib import (
    ActionReason,
    Arguments,
    BannedMember,
    Database,
    FutureTime,
    MemberID,
    can_execute_action,
    check_if_user_joined_a_stage,
    check_if_user_joined_a_voice,
    format_relative,
    has_guild_permissions,
    has_permissions,
    plural,
    EmbedPaginator,
    ErrorEmbed,
    Embed, SuccessEmbed
)

if TYPE_CHECKING:
    from lib import Context

    from ... import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class Moderation(commands.Cog):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.description = "Some simple moderation commands"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(
            name="discord_certified_moderator", id=922030031146995733
        )

    async def database_class(self):
        return await self.bot.db.new(
            Database.database_category_name.value, Database.database_channel_name.value
        )

    # set delay
    @commands.command(usage="<time in seconds>")
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def setdelay(self, ctx: "Context", seconds: int):
        """Sets Slowmode Of A Channel"""
        if not await ctx.prompt(
            f"Are you sure that you want to **add delay** of {seconds} seconds to this channel?",
            author_id=ctx.author.id,
        ):
            return
        current_slow = ctx.channel.slowmode_delay
        if current_slow == seconds:
            return await ctx.send(
                f"Sorry, But this channel already has {seconds} set as the delay! (I don't want to waste my api calls lmao)"
            )
        message = f"Set the slowmode delay in this channel to {seconds} seconds!"
        if seconds == 0:
            message = f"Reset slowmode of channel {ctx.channel.name}"
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
    async def kick(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason=None,
    ):
        """A command which kicks a given user"""

        if not await ctx.prompt(
            f"Are you sure that you want to **kick** {member} from the guild?",
            author_id=ctx.author.id,
        ):
            return
        await ctx.guild.kick(user=member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} kicked: {member.name}", description=reason
        )
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
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """A command which bans a given user"""

        if not await ctx.prompt(
            f"Are you sure that you want to **ban** {member} from the guild?",
            author_id=ctx.author.id,
        ):
            return
        if member is ctx.message.author:
            await ctx.send(embed=ErrorEmbed(description="You **can't ban yourself**!"))
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
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        embed = ErrorEmbed(
            title=f"{ctx.author.name} banned: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    # banlist
    @commands.command(
        name="banlist",
        usage="[member.id ,member.mention or member.name.with.tag]",
    )
    @commands.bot_has_permissions()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def banlist(
        self, ctx: "Context", *, member: Union[commands.MemberConverter, MemberID]
    ):
        """Shows list of users who have been banned! Or position of a specified user who was banned!"""
        banned_users = list(await ctx.guild.bans())
        if member is not None:
            if len(banned_users) == 0:
                await ctx.send(
                    embed=discord.Embed(
                        description="There is **no-one banned**! :zero: people are **banned**"
                    )
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

                    embed = ErrorEmbed(
                        title="Those who were banned are:", description=description
                    )
                    pages.append(embed)

                paginator = EmbedPaginator(ctx=ctx, entries=pages)
                await paginator.start()
            else:
                description = ""
                for k, i in enumerate(banned_users):
                    description += f"\n{k+1}. - **{i.user}** : ID [ **{banned_users[k].user.id}** ] "
                embed = ErrorEmbed(
                    title="Those who were banned are:", description=description
                )
                pages.append(embed)
                await ctx.send(embed=embed)
                return
        else:
            for i, ban_entry in enumerate(banned_users):
                user = ban_entry.user
                embed = ErrorEmbed(topic=f"About the ban {member}")
                if user is member:
                    if ban_entry.reason:
                        embed.add_field(
                            name="**Reason**", value=ban_entry.reason, inline=True
                        )
                    embed.add_field(name="**Position**", value=i + 1, inline=True)
                    embed.add_field(
                        name="**Banned User Name**",
                        value=ban_entry.user,
                        inline=True,
                    )
                    embed.set_thumbnail(url=ban_entry.user.avatar.url)
                    await ctx.channel.send(embed=embed)
                    return
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"The **{member}** isn't there in the **ban list**"
                )
            )

    # Soft Ban
    @commands.command()
    @commands.guild_only()
    @has_permissions(kick_members=True)
    async def softban(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Soft bans a member from the server.

        A softban is basically banning the member from the server but
        then unbanning the member as well. This allows you to essentially
        kick the member while removing their messages.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must have Kick Members permissions.
        """

        if not await ctx.prompt(
            f"Are you sure that you want to **softban** {member} from the guild?",
            author_id=ctx.author.id,
        ):
            return

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        await ctx.guild.ban(member, reason=reason)
        await ctx.guild.unban(member, reason=reason)
        await ctx.send("\N{OK HAND SIGN}", delete_after=4)

    # Unban
    @commands.command()
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def unban(
        self, ctx: "Context", member: BannedMember, *, reason: ActionReason = None
    ):
        """Unbans a member from the server.

        You can pass either the ID of the banned member or the Name#Discrim
        combination of the member. Typically the ID is easiest to use.

        In order for this to work, the bot must have Ban Member permissions.

        To use this command you must have Ban Members permissions.
        """
        if not await ctx.prompt(
            f"Are you sure that you want to **unban** {member.user} from the guild?",
            author_id=ctx.author.id,
        ):
            return

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        await ctx.guild.unban(member.user, reason=reason)
        if member.reason:
            await ctx.send(
                f"Unbanned {member.user} (ID: {member.user.id}), previously banned for {member.reason}."
            )
        else:
            await ctx.send(f"Unbanned {member.user} (ID: {member.user.id}).")

    # ban
    @commands.Cog.listener()
    async def on_member_ban(
        self, guild: discord.Guild, user: Union[discord.User, discord.Member]
    ):
        database = await self.database_class()
        if (
            await database.get(guild.id) is None
            or (await database.get(guild.id)).get("ban") is None
        ):
            return

        ban = self.bot.get_channel((await database.get(guild.id)).get("ban"))
        ban_entry = await guild.fetch_ban(discord.Object(id=user.id))

        e = ErrorEmbed(
            title=f"{user} was banned!",
            description=f"ID: {user.id}",
        )
        e.set_author(name=user.display_name, icon_url=user.display_avatar.url)
        if ban_entry.reason:
            e.add_field(name="**Reason** :", value=ban_entry.reason)
        try:
            await user.send(f"You were **banned** from **{guild.name}**", embed=e)
            dmed = True
        except:
            dmed = False
        e.description += "\n**DM-Members**: " + "\U00002611" if dmed else "\U0000274c"
        await ban.send(embed=e)

    # unban
    @commands.Cog.listener()
    async def on_member_unban(
        self, guild: discord.Guild, user: Union[discord.User, discord.Member]
    ):
        database = await self.database_class()
        if (
            await database.get(guild.id) is None
            or (await database.get(guild.id)).get("unban") is None
        ):
            return

        unban = self.bot.get_channel((await database.get(guild.id)).get("unban"))
        try:
            event = await guild.audit_logs().find(
                lambda x: x.action is discord.AuditLogAction.unban
            )
        except:
            event = False

        e = Embed(
            title="Unban :tada:",
            description=f"**{user}** was unbanned! :tada:",
        )
        if user.avatar.url:
            e.set_thumbnail(url=user.avatar.url)
        if event and event.reason:
            e.add_field(name="**Reason** :", value=event.reason)
        await unban.send(embed=e)
        try:
            await user.send(
                f"You were **unbanned** from **{guild.name}** ! :tada:", embed=e
            )
            dmed = True
        except:
            dmed = False
        e.description += "\n**DM-Members**: " + "\U00002611" if dmed else "\U0000274c"

    # Add Roles
    @commands.command(
        pass_context=True, usage="<member.mention> <role>", alias=["add_roles"]
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    async def ar(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        role: commands.RoleConverter,
        *,
        reason: ActionReason = None,
    ):
        """Adds a role to a given user"""
        if member is None:
            member = ctx.message.author

        role = ctx.get_roles(role)

        if not await ctx.prompt(
            f"Are you sure that you want to **add** {role} **role** to {member}?",
            author_id=ctx.author.id,
        ):
            return

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.add_roles(role, atomic=True, reason=reason)
        embed = discord.Embed(
            title="Added Roles",
            description=f"I have added the role '{role.mention}' to {member.mention}!",
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def multiban(
        self,
        ctx: "Context",
        members: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Bans multiple members from the server.
        This only works through banning via ID.
        In order for this to work, the bot must have Ban Member permissions.
        To use this command you must have Ban Members permission.
        """
        if not await ctx.prompt(
            "Are you sure that you want to **ban multiple** members?",
            author_id=ctx.author.id,
        ):
            return

        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"

        total_members = len(members)
        if total_members == 0:
            return await ctx.send("Missing members to ban.")

        confirm = await ctx.prompt(
            f"This will ban **{plural(total_members):member}**. Are you sure?",
            reacquire=False,
        )
        if not confirm:
            return await ctx.send("Aborting.")

        failed = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                failed += 1

        await ctx.send(f"Banned {total_members - failed}/{total_members} members.")

    @commands.command()
    @commands.guild_only()
    @has_permissions(ban_members=True)
    async def massban(self, ctx: "Context", *, args):
        """Mass bans multiple members from the server.
        This command has a powerful "command line" syntax. To use this command
        you and the bot must both have Ban Members permission. **Every option is optional.**
        Users are only banned **if and only if** all conditions are met.
        The following options are valid.
        `--channel` or `-c`: Channel to search for message history.
        `--reason` or `-r`: The reason for the ban.
        `--regex`: Regex that usernames must match.
        `--created`: Matches users whose accounts were created less than specified minutes ago.
        `--joined`: Matches users that joined less than specified minutes ago.
        `--joined-before`: Matches users who joined before the member ID given.
        `--joined-after`: Matches users who joined after the member ID given.
        `--no-avatar`: Matches users who have no avatar. (no arguments)
        `--no-roles`: Matches users that have no role. (no arguments)
        `--show`: Show members instead of banning them (no arguments).
        Message history filters (Requires `--channel`):
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--match`: A regex to match the message content to.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        `--files`: Checks if the message has attachments (no arguments).
        `--embeds`: Checks if the message has embeds (no arguments).
        """

        if not await ctx.prompt(
            "Are you sure that you want to **massban**?", author_id=ctx.author.id
        ):
            return

        # For some reason there are cases due to caching that ctx.author
        # can be a User even in a guild only context
        # Rather than trying to work out the kink with it
        # Just upgrade the member itself.
        if not isinstance(ctx.author, discord.Member):
            try:
                author = await ctx.guild.fetch_member(ctx.author.id)
            except discord.HTTPException:
                return await ctx.send(
                    "Somehow, Discord does not seem to think you are in this server."
                )
        else:
            author = ctx.author

        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument("--channel", "-c")
        parser.add_argument("--reason", "-r")
        parser.add_argument("--search", type=int, default=100)
        parser.add_argument("--regex")
        parser.add_argument("--no-avatar", action="store_true")
        parser.add_argument("--no-roles", action="store_true")
        parser.add_argument("--created", type=int)
        parser.add_argument("--joined", type=int)
        parser.add_argument("--joined-before", type=int)
        parser.add_argument("--joined-after", type=int)
        parser.add_argument("--contains")
        parser.add_argument("--starts")
        parser.add_argument("--ends")
        parser.add_argument("--match")
        parser.add_argument("--show", action="store_true")
        parser.add_argument(
            "--embeds", action="store_const", const=lambda m: len(m.embeds)
        )
        parser.add_argument(
            "--files", action="store_const", const=lambda m: len(m.attachments)
        )
        parser.add_argument("--after", type=int)
        parser.add_argument("--before", type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            return await ctx.send(str(e))

        members = []

        if args.channel:
            channel = await commands.TextChannelConverter().convert(ctx, args.channel)
            before = args.before and discord.Object(id=args.before)
            after = args.after and discord.Object(id=args.after)
            predicates = []
            if args.contains:
                predicates.append(lambda m: args.contains in m.content)
            if args.starts:
                predicates.append(lambda m: m.content.startswith(args.starts))
            if args.ends:
                predicates.append(lambda m: m.content.endswith(args.ends))
            if args.match:
                try:
                    _match = re.compile(args.match)
                except re.error as e:
                    return await ctx.send(f"Invalid regex passed to `--match`: {e}")
                else:
                    predicates.append(lambda m, x=_match: x.match(m.content))
            if args.embeds:
                predicates.append(args.embeds)
            if args.files:
                predicates.append(args.files)

            async for message in channel.history(
                limit=min(max(1, args.search), 2000), before=before, after=after
            ):
                if all(p(message) for p in predicates):
                    members.append(message.author)
        else:
            if ctx.guild.chunked:
                members = ctx.guild.members
            else:
                async with ctx.typing():
                    await ctx.guild.chunk(cache=True)
                members = ctx.guild.members

        # member filters
        predicates = [
            lambda m: isinstance(m, discord.Member)
            and can_execute_action(ctx, author, m),  # Only if applicable
            lambda m: not m.bot,  # No bots
            lambda m: m.discriminator != "0000",  # No deleted users
        ]

        converter = commands.MemberConverter()

        if args.regex:
            try:
                _regex = re.compile(args.regex)
            except re.error as e:
                return await ctx.send(f"Invalid regex passed to `--regex`: {e}")
            else:
                predicates.append(lambda m, x=_regex: x.match(m.name))

        if args.no_avatar:
            predicates.append(lambda m: m.avatar is None)
        if args.no_roles:
            predicates.append(lambda m: len(getattr(m, "roles", [])) <= 1)

        now = discord.utils.utcnow()
        if args.created:

            def created(
                member, *, offset=now - datetime.timedelta(minutes=args.created)
            ):
                return member.created_at > offset

            predicates.append(created)
        if args.joined:

            def joined(member, *, offset=now - datetime.timedelta(minutes=args.joined)):
                if isinstance(member, discord.User):
                    # If the member is a user then they left already
                    return True
                return member.joined_at and member.joined_at > offset

            predicates.append(joined)
        if args.joined_after:
            _joined_after_member = await converter.convert(ctx, str(args.joined_after))

            def joined_after(member, *, _other=_joined_after_member):
                return (
                    member.joined_at
                    and _other.joined_at
                    and member.joined_at > _other.joined_at
                )

            predicates.append(joined_after)
        if args.joined_before:
            _joined_before_member = await converter.convert(
                ctx, str(args.joined_before)
            )

            def joined_before(member, *, _other=_joined_before_member):
                return (
                    member.joined_at
                    and _other.joined_at
                    and member.joined_at < _other.joined_at
                )

            predicates.append(joined_before)

        members = {m for m in members if all(p(m) for p in predicates)}
        if len(members) == 0:
            return await ctx.send("No members found matching criteria.")

        if args.show:
            members = sorted(members, key=lambda m: m.joined_at or now)
            fmt = "\n".join(
                f"{m.id}\tJoined: {m.joined_at}\tCreated: {m.created_at}\t{m}"
                for m in members
            )
            content = f"Current Time: {discord.utils.utcnow()}\nTotal members: {len(members)}\n{fmt}"
            file = discord.File(
                io.BytesIO(content.encode("utf-8")), filename="members.txt"
            )
            return await ctx.send(file=file)

        if args.reason is None:
            return await ctx.send("--reason flag is required.")
        else:
            reason = await ActionReason().convert(ctx, args.reason)

        confirm = await ctx.prompt(
            f"This will ban **{plural(len(members)):member}**. Are you sure?"
        )
        if not confirm:
            return await ctx.send("Aborting.")

        count = 0
        for member in members:
            try:
                await ctx.guild.ban(member, reason=reason)
            except discord.HTTPException:
                pass
            else:
                count += 1

        await ctx.send(f"Banned {count}/{len(members)}")

    # Warn
    @commands.command(pass_context=True, usage="<member.mention> [optional: reason]")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def warn(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: Optional[str] = None,
    ):
        """Warn a user"""
        data = await (await self.database_class()).get(ctx.guild.id)
        if data is None or data.get("warns") is None:
            e = ErrorEmbed(
                title=f"No warning system setup for the {ctx.guild.name}",
                description="You can always setup the **warning system** by running `{}setup add warns #warns`".format(
                    ctx.prefix
                ),
            )
            await ctx.send(embed=e, delete_after=10)
            return

        if not await ctx.prompt(
            f"Are you sure that you want to **warn** {member}?", author_id=ctx.author.id
        ):
            return

        e = ErrorEmbed(title="You have been warned!")
        e.add_field(
            name="**Responsible Moderator**:",
            value=ctx.message.author.mention,
            inline=True,
        )
        if reason:
            e.add_field(name="**Reason**:", value=reason, inline=True)

        warning_channel = self.bot.get_channel(data.get("warns"))
        await member.send(embed=e)
        await warning_channel.send(embed=e, content=member.mention)
        await ctx.send(
            f"{member.mention} has been **warned** by you ||{ctx.author.mention}||",
            delete_after=10,
        )

    @commands.command(pass_context=True, usage="[member.mention]")
    @commands.guild_only()
    async def warnlist(
        self,
        ctx: "Context",
        member: Optional[Union[commands.MemberConverter, MemberID]] = None,
    ):
        """Get the no. of warns for a specified user"""
        data = await (await self.database_class()).get(ctx.guild.id)
        if data is None or data.get("warns") is None:
            e = ErrorEmbed(
                title=f"No warning system setup for the {ctx.guild.name}",
                description="You can always setup the **warning system** by running `{}setup add warns #warns` command".format(
                    ctx.prefix
                ),
            )
            await ctx.send(embed=e, delete_after=10)
            return

        member = member or ctx.message.author
        embed = discord.Embed(title="Type the below message in the search bar")
        search_image = discord.File(
            join(self.bot.minato_dir, "discord", "search.png"), filename="search.png"
        )
        embed.set_image(url="attachment://search.png")
        await ctx.send(file=search_image, embed=embed)

        warning_channel = self.bot.get_channel(data.get("warns"))
        message = f"mentions: {member}  in: {warning_channel}"
        await ctx.send(message)

    @commands.command(aliases=["newmembers"], usage="[count]")
    @commands.guild_only()
    async def newusers(self, ctx: "Context", *, count: Optional[int] = 5):
        """
        Tells you the newest members of the server.

        This is useful to check if any suspicious members have
        joined.

        The count parameter clamps the number in between 5 - 25
        """
        count = max(min(count, 25), 5)

        if not ctx.guild.chunked:
            members = await ctx.guild.chunk(cache=True)

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[
            :count
        ]

        embed = discord.Embed(title="New Members", colour=discord.Colour.green())

        for member in members:
            joined = member.joined_at.strftime("%a, %d %B %Y %I:%M:%S %fms %Z")
            created = member.created_at.strftime("%a, %d %B %Y %I:%M:%S %fms %Z")
            body = f"Joined: {joined}\nCreated: {created}"
            embed.add_field(
                name=f"{member} (ID: {member.id})", value=body, inline=False
            )

        await ctx.send(embed=embed)

    @staticmethod
    async def _basic_cleanup_strategy(ctx: "Context", search):
        count = 0
        async for msg in ctx.history(limit=search, before=ctx.message):
            if msg.author == ctx.me and not (msg.mentions or msg.role_mentions):
                await msg.delete()
                count += 1
        return {"Bot": count}

    async def _complex_cleanup_strategy(self, ctx: "Context", search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))  # thanks startswith

        def check(m):
            return m.author == ctx.me or m.content.startswith(prefixes)

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    async def _regular_user_cleanup_strategy(self, ctx: "Context", search):
        prefixes = tuple(self.bot.get_guild_prefixes(ctx.guild))

        def check(m):
            return (m.author == ctx.me or m.content.startswith(prefixes)) and not (
                m.mentions or m.role_mentions
            )

        deleted = await ctx.channel.purge(limit=search, check=check, before=ctx.message)
        return Counter(m.author.display_name for m in deleted)

    @commands.command()
    async def cleanup(self, ctx: "Context", search=100):
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
        if not await ctx.prompt(
            "Are you sure that you want to **cleanup** the bot's messages from this channel?",
            author_id=ctx.author.id,
        ):
            return

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
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await ctx.send("\n".join(messages), delete_after=10)

    @commands.command(
        name="simeplepurge",
        description="A command which purges the channel it is called in",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx: "Context", amount=5):
        """A command which purges the channel it is called in"""
        if not await ctx.prompt(
            f"Are you sure that you want to **purge** {amount} **messages**?",
            author_id=ctx.author.id,
        ):
            return

        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"{amount} messages were cleared",
        )
        await ctx.send(embed=embed, delete_after=4)

    @commands.group(aliases=["purge"])
    @commands.guild_only()
    @has_permissions(manage_messages=True)
    async def remove(self, ctx: "Context"):
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
            return

    @staticmethod
    async def do_removal(ctx: "Context", limit, predicate, *, before=None, after=None):
        if not await ctx.prompt(
            "Are you sure that you want to **remove the messages**?",
            author_id=ctx.author.id,
        ):
            return
        if limit > 2000:
            return await ctx.send(f"Too many messages to search given ({limit}/2000)")

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(
                limit=limit, before=before, after=after, check=predicate
            )
        except discord.Forbidden as e:
            return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"**{name}**: {count}" for name, count in spammers)

        to_send = "\n".join(messages)

        if len(to_send) > 2000:
            await ctx.send(f"Successfully removed {deleted} messages.", delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @remove.command()
    async def embeds(self, ctx: "Context", search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command()
    async def files(self, ctx: "Context", search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command()
    async def images(self, ctx: "Context", search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(
            ctx, search, lambda e: len(e.embeds) or len(e.attachments)
        )

    @remove.command(name="all")
    async def _remove_all(self, ctx: "Context", search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command()
    async def user(self, ctx: "Context", member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command()
    async def contains(self, ctx: "Context", *, substr: str):
        """Removes all messages containing a substring.

        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @remove.command(name="bot", aliases=["bots"])
    async def _bot(self, ctx: "Context", prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (
                prefix and m.content.startswith(prefix)
            )

        await self.do_removal(ctx, search, predicate)

    @remove.command(name="emoji", aliases=["emojis"])
    async def _emoji(self, ctx: "Context", search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @remove.command(name="reactions")
    async def _reactions(self, ctx: "Context", search=100):
        """Removes all reactions from messages that have them."""
        if not await ctx.prompt(
            "Are you sure that you want to **remove the reactions**?",
            author_id=ctx.author.id,
        ):
            return

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if message.reactions:
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")

    @remove.command()
    async def custom(self, ctx: "Context", *, args: str):
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
        if not await ctx.prompt(
            "Are you sure that you want to **remove the messages**?",
            author_id=ctx.author.id,
        ):
            return

        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument("--user", nargs="+")
        parser.add_argument("--contains", nargs="+")
        parser.add_argument("--starts", nargs="+")
        parser.add_argument("--ends", nargs="+")
        parser.add_argument("--or", action="store_true", dest="_or")
        parser.add_argument("--not", action="store_true", dest="_not")
        parser.add_argument("--emoji", action="store_true")
        parser.add_argument("--bot", action="store_const", const=lambda m: m.author.bot)
        parser.add_argument(
            "--embeds", action="store_const", const=lambda m: len(m.embeds)
        )
        parser.add_argument(
            "--files", action="store_const", const=lambda m: len(m.attachments)
        )
        parser.add_argument(
            "--reactions", action="store_const", const=lambda m: len(m.reactions)
        )
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
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(
                lambda m: any(m.content.startswith(s) for s in args.starts)
            )

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

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
        await self.do_removal(
            ctx, args.search, predicate, before=args.before, after=args.after
        )

    @commands.command(aliases=["mute"])
    @commands.guild_only()
    @commands.has_guild_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx: "Context",
        duration: FutureTime,
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Timeout the member for a specified duration of time"""
        if not await ctx.prompt(
            f"Are you sure that you want to **time out** {member} until {format_relative(duration.dt)}?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(timed_out_until=duration.dt, reason=reason)
        await ctx.send(
            embed=ErrorEmbed(
                description=f"**Timed out** {member} until {format_relative(duration.dt)}"
            )
        )

    @commands.command(aliases=["unmute"])
    @commands.guild_only()
    @commands.has_guild_permissions(moderate_members=True)
    @has_permissions(moderate_members=True)
    async def untimeout(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Removes timeout from the member"""
        if not await ctx.prompt(
            f"Are you sure that you want to **remove the time out** {member} ?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(timed_out_until=discord.utils.utcnow(), reason=reason)
        await ctx.send(
            embed=SuccessEmbed(description=f"**Removed timed out** from {member}")
        )

    @commands.command(aliases=["vcmute"])
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    @has_permissions(mute_members=True)
    @commands.check(check_if_user_joined_a_voice)
    async def voicemute(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Mutes the members from all the voice channels"""
        if not await ctx.prompt(
            f"Are you sure that you want to **mute** {member} from `all voice channels`?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(mute=True, reason=reason)
        await ctx.send(
            embed=ErrorEmbed(
                description=f"**Muted** {member} from `all voice channels`"
            )
        )

    @commands.command(aliases=["vcunmute"])
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    @has_permissions(mute_members=True)
    @commands.check(check_if_user_joined_a_voice)
    async def voiceunmute(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Unmutes the members all from the voice channels"""
        if not await ctx.prompt(
            f"Are you sure that you want to **unmute** {member} from `all voice channels`?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(mute=False, reason=reason)
        await ctx.send(
            embed=SuccessEmbed(
                description=f"**Unmuted** {member} from `all voice channels`"
            )
        )

    @commands.command(aliases=["serverdeaf"])
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    @has_permissions(deafen_members=True)
    @commands.check(check_if_user_joined_a_voice)
    async def serverdeafen(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Deafens the member from all the voice channels"""
        if not await ctx.prompt(
            f"Are you sure that you want to **deafen** {member}?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(deafen=True, reason=reason)
        await ctx.send(embed=ErrorEmbed(description=f"**Deafend** {member}"))

    @commands.command(aliases=["serverundeaf"])
    @commands.guild_only()
    @commands.has_guild_permissions(deafen_members=True)
    @has_permissions(deafen_members=True)
    @commands.check(check_if_user_joined_a_voice)
    async def serverundeafen(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Un-deafen the member all from the server"""
        if not await ctx.prompt(
            f"Are you sure that you want to **un-deafen** {member}?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(deafen=False, reason=reason)
        await ctx.send(embed=SuccessEmbed(description=f"**Un-Deafend** {member}"))

    @commands.command(aliases=["stagesuppress", "stagemute"])
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    @has_permissions(mute_members=True)
    @commands.check(check_if_user_joined_a_stage)
    async def suppress(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Suppresses the members from all the stage channels"""
        if not await ctx.prompt(
            f"Are you sure that you want to **suppress** {member} from `all stage channels`?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(suppress=True, reason=reason)
        await ctx.send(
            embed=ErrorEmbed(
                description=f"**Suppressed** {member} from `all stage channels`"
            )
        )

    @commands.command(aliases=["stageunsuppress", "stageunmute"])
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    @has_permissions(mute_members=True)
    @commands.check(check_if_user_joined_a_stage)
    async def unsuppress(
        self,
        ctx: "Context",
        member: Union[commands.MemberConverter, MemberID],
        *,
        reason: ActionReason = None,
    ):
        """Un-Suppresses the members from all the stage channels"""
        if not await ctx.prompt(
            f"Are you sure that you want to **un-suppress** {member} from `all stage channels`?",
            author_id=ctx.author.id,
        ):
            return
        if reason is None:
            reason = f"Action done by {ctx.author} (ID: {ctx.author.id})"
        await member.edit(suppress=False, reason=reason)
        await ctx.send(
            embed=SuccessEmbed(
                description=f"**Un-Suppressed** {member} from `all stage channels`"
            )
        )

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def lock(self, ctx: "Context"):
        """Locking Commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @lock.command(aliases=["thread"], usage="[thread.channel]")
    @commands.has_guild_permissions(manage_threads=True)
    async def threadchannel(
        ctx: "Context", channels: commands.Greedy[discord.Thread] = None
    ):
        """Locks the specified thread channel(s), both member and bot required `Manage Thread` perms to operate"""
        if channels is None:
            if not isinstance(ctx.channel, discord.Thread):
                await ctx.send(
                    embed=ErrorEmbed(description="The channel is not a `Thread`")
                )
                return
            channels = [ctx.channel]
        for channel in channels:
            await channel.edit(locked=True, archived=True)
        await ctx.send(f'{" ,".join(list(map(lambda a: a.mention, channels)))} locked.')

    @lock.command(aliases=["text"], usage="[text.channel]")
    @has_guild_permissions(manage_channels=True)
    async def textchannel(
        ctx: "Context", channels: commands.Greedy[discord.TextChannel] = None
    ):
        """Locks the specified text channel(s), both member and bot required `Manage Channel` perms to operate"""
        if channels is None:
            channels = [ctx.channel]
        for channel in channels:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = False
            await channel.edit(
                overwrites={ctx.guild.default_role: overwrite},
                reason=f"Action initiated by {ctx.author} (ID: {ctx.author.id})",
            )
        await ctx.send(f'{" ,".join(list(map(lambda a: a.mention, channels)))} locked.')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def unlock(self, ctx: "Context"):
        """Unlocking Commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @unlock.command(aliases=["thread"], usage="[thread.channel]")
    @has_guild_permissions(manage_threads=True)
    async def threadchannel(self, ctx: "Context"):
        """Unlocks the  thread channel in which the command was rrun, both member and bot required `Manage Thread` perms to operate"""
        if not isinstance(ctx.channel, discord.Thread):
            await ctx.send(
                embed=ErrorEmbed(description="The channel is not a `Thread`")
            )
            return
        await ctx.channel.edit(locked=False, archived=False)
        await ctx.send(f"{ctx.channel.mention} unlocked.")

    @unlock.command(aliases=["text"], usage="[text.channel]")
    @has_guild_permissions(manage_channels=True)
    async def textchannel(
        self,
        ctx: "Context",
        channels: commands.Greedy[discord.TextChannel] = None,
    ):
        """Unlocks the specified text channel(s), both member and bot required `Manage Channel` perms to operate"""
        if channels is None:
            channels = [ctx.channel]
        for channel in channels:
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True
            await channel.edit(
                overwrites={ctx.guild.default_role: overwrite},
                reason=f"Action initiated by {ctx.author} (ID: {ctx.author.id})",
            )
        await ctx.send(
            f'{" ,".join(list(map(lambda a: a.mention, channels)))} unlocked.'
        )

    @commands.command(aliases=["threadjoin"])
    @commands.guild_only()
    async def jointhread(self, ctx: "Context", channel: discord.Thread):
        """Joins the specified thread"""
        if not isinstance(channel, discord.Thread):
            await ctx.send(
                embed=ErrorEmbed(description="The channel is not a `Thread`")
            )
            return
        await channel.send("Hey!")
        try:
            await ctx.message.delete(
                reason="Just to indicate that the command was successfully completed"
            )
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Moderation(bot))
