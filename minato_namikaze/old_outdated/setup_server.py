from __future__ import annotations

import json
import string
import typing
from datetime import timedelta
from json.decoder import JSONDecodeError

import discord
from discord.ext import commands
from discord.ext import tasks
from minato_namikaze.lib import detect_bad_domains
from minato_namikaze.lib import Embed
from minato_namikaze.lib import EmbedPaginator
from minato_namikaze.lib import ErrorEmbed
from minato_namikaze.lib import is_mod
from minato_namikaze.lib import StarboardEmbed

if typing.TYPE_CHECKING:
    from lib import Context

    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Do some necessary setup through an interactive mode."
        self.cleanup.start()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{HAMMER AND WRENCH}")

    async def add_and_check_data(self, dict_to_add: dict, ctx: "Context") -> None:
        database = await self.database_class()
        guild_dict = await database.get(ctx.guild.id)
        if guild_dict is None:
            await database.set(ctx.guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await database.set(ctx.guild.id, guild_dict)
        await ctx.send(":ok_hand:")
        return

    @tasks.loop(hours=1, reconnect=True)
    async def cleanup(self):
        database = await self.database_class()
        async for message in database._Database__channel.history(limit=None):
            cnt = message.content
            try:
                data = json.loads(str(cnt))
                data.pop("type")
                data_keys = list(map(str, list(data.keys())))
                try:
                    await commands.GuildConverter().convert(
                        await self.bot.get_context(message),
                        str(data_keys[0]),
                    )
                except (commands.CommandError, commands.BadArgument):
                    if not self.bot.local:
                        await message.delete()
            except JSONDecodeError:
                if not self.bot.local:
                    await message.delete()

    @commands.group()
    @commands.guild_only()
    @is_mod()
    async def setup(self, ctx: "Context"):
        """
        This commands setups some logging system for system for server with some nice features
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return

    @setup.command(usage="<add_type> <textchannel>")
    async def add(
        self,
        ctx: "Context",
        add_type: typing.Literal["ban", "feedback", "warns", "unban"],
        channel: commands.TextChannelConverter,
    ):
        """
        This command adds logging of the following things in the specified text channel
        >   - ban
        >   - warns
        >   - unban
        >   - feedback

        `If the data for the any of the above is already available in database then it rewrite the data.`

        Example usage:
            ``)add ban #bans``
        """

        if not await ctx.prompt(
            f"Do you really want to **log {add_type}** for **{ctx.guild.name}** in {channel.mention}?",
        ):
            return
        dict_to_add = {str(add_type): channel.id}
        await self.add_and_check_data(dict_to_add=dict_to_add, ctx=ctx)

    @setup.command(usage="<textchannel.mention> <support_required_role>")
    async def support(
        self,
        ctx: "Context",
        textchannel: commands.TextChannelConverter,
        support_required_role: commands.RoleConverter,
    ):
        """
        Creates a **public support system** in an interactive manner.

        Args:
            - textchannel : A text channel where the support request will be logged.
            - support_required_role : A role which will be provided to the users, when a support request lodged
        """
        if not await ctx.prompt(
            f"Do you really want to **create a suppoprt system** for **{ctx.guild.name}** in {textchannel.mention}?",
        ):
            return
        dict_to_add = {"support": [textchannel.id, support_required_role.id]}
        await self.add_and_check_data(dict_to_add=dict_to_add, ctx=ctx)

    @setup.command(usage="<option> [action] [logging_channel]")
    async def badlinks(
        self,
        ctx: "Context",
        action: None | (typing.Literal["ban", "mute", "timeout", "kick", "log"]) = None,
        logging_channel: commands.TextChannelConverter | None = None,
        option: typing.Literal["yes", "no", "on", "off", True, False] = True,
    ):
        """
        If enabled then it checks against any scam, phishing or adult links which is posted by members and take actions accordingly

        Args:
            - action [Optional] (default: log) : What kind of action to take, It accepts the following options ; 'ban', 'mute', 'timeout', 'kick', 'log'
            - logging_channel [Optional] : It will log in a specific channel if specified, otherwise it will log the message where the link was sent.
            - option [Optional] (default: True) : It accepts the following options ; True, False, yes, no, on, off

        `Note: If 'log' action is selected then, I will only delete the message and log it the current channel where the link was sent and will do nothing`
        """
        if option is not None and option in ["no", "off", False]:
            database = await self.database_class()
            guild_dict = await database.get(ctx.guild.id)
            if guild_dict is None:
                return
            guild_dict.pop("badlinks")
            await database.set(ctx.guild.id, guild_dict)
            await ctx.send(":ok_hand:")
            return
        await self.add_and_check_data(
            {
                "badlinks": {
                    "option": option,
                    "action": action,
                    "logging_channel": (
                        logging_channel.id
                        if logging_channel is not None
                        else logging_channel
                    ),
                },
            },
            ctx=ctx,
        )

    @setup.command(usage="<channel> [no_of_stars] [self_star] [ignore_nsfw]")
    async def starboard(
        self,
        ctx: "Context",
        channel: commands.TextChannelConverter | discord.TextChannel,
        no_of_stars: int | None = 5,
        self_star: bool | None = False,
        ignore_nsfw: bool | None = True,
    ):
        """
        Setups the starboard in your server.
        It posts the message in the specified channel whenever someone stars a message using \U00002b50 emoji

        Args:
            - channel : The channel where the starred message will go
            - no_of_stars [Optional] [int] : Minimum number of stars required before posting it to the specified channel
            - self_star [Optional] [bool] (default: False) : Whether self  starring of message should be there or not
            - ignore_nsfw [Optional] [bool] (default: True) : Whether to ignore NSFW channels or not
        """
        await self.add_and_check_data(
            {
                "starboard": {
                    "channel": channel.id,
                    "no_of_stars": no_of_stars,
                    "self_star": self_star,
                    "ignore_nsfw": ignore_nsfw,
                },
            },
            ctx=ctx,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message is None
            or message.content == string.whitespace
            or message.content is None
        ):
            return
        ctx = await self.bot.get_context(message)
        detected_urls = await detect_bad_domains(
            discord.utils.remove_markdown(message.content),
        )
        if len(detected_urls) <= 0:
            return
        embed = ErrorEmbed(title="SCAM/PHISHING/ADULT LINK(S) DETECTED")
        detected_string = "\n".join([f"- ||{i}||" for i in set(detected_urls)])
        embed.description = (
            f"The following scam url(s) were detected:\n{detected_string}"
        )
        embed.set_author(
            name=message.author,
            icon_url=message.author.display_avatar.url,
        )
        message_sent = await ctx.send(embed=embed)
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            pass

        if message.guild is None:
            return

        database = await self.database_class()
        guild_dict = await database.get(message.guild.id)
        if guild_dict is None:
            return

        bad_link_config: dict = guild_dict.get("badlinks")
        if bad_link_config is None:
            return

        action_config = bad_link_config.get("action")
        action_reason_string = "[Auto Mod] Scam/Phishing/Adult Link posted"
        if action_config is None:
            return

        if action_config.lower() == "ban":
            try:
                await message.author.ban(reason=action_reason_string)
                embed.add_field(name="Action Taken", value="Ban :hammer:")
                await message_sent.edit(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass
        if action_config.lower() in ["mute", "timeout"]:
            try:
                await message.author.edit(
                    timed_out_until=discord.utils.utcnow() + timedelta(days=2),
                    reason=action_reason_string,
                )
                embed.add_field(name="Action Taken", value="Time Out :x:")
                await message_sent.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass
        if action_config.lower() == "kick":
            try:
                await message.author.kick(reason=action_reason_string)
                embed.add_field(name="Action Taken", value="Kick :foot:")
                await message_sent.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

        log_config = bad_link_config.get("logging_channel")
        if log_config is None:
            return

        log_channel = await self.bot.fetch_channel(log_config)
        await log_channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @is_mod()
    async def raw_data(self, ctx: "Context"):
        """
        It returns the raw data which is stored in the database in the form of json
        """
        embed = Embed(title=f"Data associated with {ctx.guild.name}")
        database = await self.database_class()
        database_antiraid = await self.database_class_antiraid()
        database_mentionspam = await self.database_class_mentionspam()

        data = await database.get(ctx.guild.id)
        data_antiraid = await database_antiraid.get(ctx.guild.id)
        data_mentionspam = await database_mentionspam.get(ctx.guild.id)

        if data is None and data_antiraid is None and data_mentionspam is None:
            embed.description = "```\nNo data associated with this guild\n```"
            await ctx.send(embed=embed)
            return

        embeds_list = []
        if data is not None:
            embed = Embed()
            embed.title = "Setup Vars"
            embed.description = "```json\n{}\n```".format(
                json.dumps(
                    {"setupvars": data},
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "),
                    ensure_ascii=False,
                    null=None,
                ),
            )
            embeds_list.append(embed)
        if data_antiraid is not None:
            embed = Embed()
            embed.title = "AntiRaid"
            embed.description = "```json\n{}\n```".format(
                json.dumps(
                    {"antiraid": data_antiraid},
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "),
                    ensure_ascii=False,
                    null=None,
                ),
            )
            embeds_list.append(embed)
        if data_mentionspam is not None:
            embed = Embed()
            embed.title = "Mention Spam"
            embed.description = "```json\n{}\n```".format(
                json.dumps(
                    {"mentionspam": data_mentionspam},
                    sort_keys=True,
                    indent=4,
                    separators=(",", ": "),
                    ensure_ascii=False,
                    null=None,
                ),
            )
            embeds_list.append(embed)

        paginator = EmbedPaginator(entries=embeds_list, ctx=ctx)
        await paginator.start()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        database = await self.database_class()
        database_antiraid = await self.database_class_antiraid()
        database_mentionspam = await self.database_class_mentionspam()

        await database.delete(guild.id)
        await database_antiraid.delete(guild.id)
        await database_mentionspam.delete(guild.id)

    @commands.command(
        alisases=["datadelete", "delete_data", "data_delete"],
        usage="[type_data]",
    )
    @commands.guild_only()
    @is_mod()
    async def deletedata(
        self,
        ctx: "Context",
        type_data: typing.Literal[
            "ban",
            "unban",
            "support",
            "warns",
            "feedback",
            "mentionspam",
            "antiraid",
            "starboard",
            "badlinks",
            "all",
        ] = "all",
    ):
        """
        This command deletes the available data:
        It accepts an optional parameter `type_data`, You can pass the following things through `type_data` parameter:

            - `ban` : Deletes the `ban data` from database
            - `unban` : Deletes the `unban data` from database
            - `support` : Deletes the `support data` from database
            - `warns` : Deletes the `warns data` from database
            - `feedback`: Deletes the `feedback data` from database
            - `mentionspam`: Deletes the `mentionspam data` from database
            - `antiraid`: Deletes the `antiraid data` from database
            - `badlinks`: Deletes the `badlinks data` from database
            - `starboard`: Deletes the `starboard data` from database

        By default the `type_data` is set to `all`, which will delete all the data present in the database.
        """
        if not await ctx.prompt(f"Do you really want to **delete {type_data}** data?"):
            return
        if type_data in [
            "ban",
            "unban",
            "support",
            "warns",
            "feedback",
            "badlinks",
            "starboard",
        ]:
            database = await self.database_class()
            data = await database.get(ctx.guild.id)
            data.pop(type_data)
            await database.set(ctx.guild.id, data)
            await ctx.send(":ok_hand:")
            return

        if type_data == "mentionspam":
            database = await self.database_class_mentionspam()
            await database.delete(ctx.guild.id)
            await ctx.send(":ok_hand:")
            return

        if type_data == "antiraid":
            database = await self.database_class_antiraid()
            await database.delete(ctx.guild.id)
            await ctx.send(":ok_hand:")
            return

        database = await self.database_class()
        database_antiraid = await self.database_class_antiraid()
        database_mentionspam = await self.database_class_mentionspam()

        await database.delete(ctx.guild.id)
        await database_antiraid.delete(ctx.guild.id)
        await database_mentionspam.delete(ctx.guild.id)
        await ctx.send(":ok_hand:")

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload: discord.RawReactionActionEvent,
    ) -> None:
        if payload.guild_id is None:
            return
        reaction = str(payload.emoji)
        if reaction != str(discord.PartialEmoji(name="\U00002b50")):
            return

        if payload.user_id == self.bot.application_id:
            return

        database = await self.database_class()
        data = await database.get(int(payload.guild_id))
        if data is None:
            return
        if data.get("starboard") is None:
            return
        data = data.get("starboard")
        if int(data.get("channel")) == int(payload.channel_id):
            return

        channel = self.bot.get_channel(payload.channel_id)
        if (
            data.get("ignore_nsfw") is not None
            and data.get("ignore_nsfw")
            and channel.is_nsfw()
        ):
            return

        msg = await channel.fetch_message(payload.message_id)
        if data.get("self_star") and int(payload.user_id) == msg.author.id:
            pass
        elif not data.get("self_star") and int(payload.user_id) == msg.author.id:
            return
        no_of_reaction = discord.utils.find(
            lambda a: str(a.emoji) == str(discord.PartialEmoji(name="\U00002b50")),
            msg.reactions,
        )
        if no_of_reaction.count < int(data.get("no_of_stars")):
            return

        embed = StarboardEmbed(timestamp=msg.created_at)
        description = msg.content
        if len(msg.embeds) > 0:
            embed_user = msg.embeds[0]
            if not isinstance(embed_user.fields, discord.embeds._EmptyEmbed):
                for i in embed_user.fields:
                    embed.add_field(name=i.name, value=i.value, inline=i.inline)
            if embed_user.title is not None or not isinstance(
                embed_user.title,
                discord.embeds._EmptyEmbed,
            ):
                if description is not None:
                    description = f"{description}\n\n**{embed_user.title}**\n{embed_user.description}"
                else:
                    description = f"**{embed_user.title}**\n{embed_user.description}"
            else:
                if description is not None:
                    description = f"{description}\n\n{embed_user.description}"
                else:
                    description = embed_user.description
            if not isinstance(embed_user.image.url, discord.embeds._EmptyEmbed):
                embed.set_image(url=embed_user.image.url)
        if (
            isinstance(embed.image.url, discord.embeds._EmptyEmbed)
            and len(msg.attachments) > 0
        ):
            attachment = msg.attachments[0]
            if attachment.content_type.lower() in [
                "image/jpeg",
                "image/avif",
                "image/png",
                "image/svg+xml",
            ]:
                embed.set_image(url=attachment.url)
            else:
                description = f"{description}\n\n**Attachment(s)**\n{attachment.url}"
        embed.description = f"{description}\n\n**Original**\n[Jump]({msg.jump_url})"
        embed.set_author(
            name=msg.author,
            icon_url=msg.author.display_avatar.url,
            url=msg.jump_url,
        )
        embed.set_footer(text=str(msg.id))

        starboard_channel = self.bot.get_channel(data.get("channel"))
        await starboard_channel.send(
            content=f"\U00002b50 {channel.mention} by {msg.author.mention}",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                users=False,
                roles=False,
                replied_user=False,
            ),
        )


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(ServerSetup(bot))
