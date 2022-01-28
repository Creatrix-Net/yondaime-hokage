import json
import typing

import discord
from discord.ext import commands

from ...lib import (
    Embed,
    EmbedPaginator,
    antiraid_channel_name,
    database_category_name,
    database_channel_name,
    is_mod,
    mentionspam_channel_name,
)


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Do some necessary setup through an interactive mode."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{HAMMER AND WRENCH}")

    async def database_class(self):
        return await self.bot.db.new(database_category_name,
                                     database_channel_name)

    async def database_class_antiraid(self):
        return await self.bot.db.new(database_category_name,
                                     antiraid_channel_name)

    async def database_class_mentionspam(self):
        return await self.bot.db.new(database_category_name,
                                     mentionspam_channel_name)

    async def add_and_check_data(self, dict_to_add: dict,
                                 ctx: commands.Context) -> None:
        database = await self.database_class()
        guild_dict = await database.get(ctx.guild.id)
        if guild_dict is None:
            await database.set(ctx.guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await database.set(ctx.guild.id, guild_dict)
        await ctx.send(":ok_hand:")
        return

    @commands.group(usage="<add_type> <textchannel>")
    @commands.guild_only()
    @is_mod()
    async def add(
        self,
        ctx,
        add_type: typing.Literal["ban", "feedback", "warns", "unban"],
        channel: commands.TextChannelConverter,
    ):
        """
        This command adds logging of the following things in the specified text channel
        >   - ban
        >   - warns
        >   - unban
        >   - feedback
        >   - support
        >   - badlinks

        `If the data for the any of the above is already available in database then it rewrite the data.`

        Example usage:
            ``)add ban #bans``
        """

        if not await ctx.prompt(
                f"Do you really want to **log {add_type}** for **{ctx.guild.name}** in {channel.mention}?"
        ):
            return
        dict_to_add = {str(add_type): channel.id}
        await self.add_and_check_data(dict_to_add=dict_to_add, ctx=ctx)

    @add.command(usage="<textchannel.mention> <support_required_role>")
    async def support(
        self,
        ctx,
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
                f"Do you really want to **create a suppoprt system** for **{ctx.guild.name}** in {textchannel.mention}?"
        ):
            return
        dict_to_add = {"support": [textchannel.id, support_required_role.id]}
        await self.add_and_check_data(dict_to_add=dict_to_add,
                                      search_query="support",
                                      ctx=ctx)

    @add.command(usage="<option> [action] [logging_channel]")
    async def badlinks(
        self,
        ctx,
        option: typing.Literal[True, False, "yes", "no", "on", "off"],
        action: typing.Optional[typing.Literal["ban", "mute", "timeout",
                                               "kick", "log"]] = "log",
        logging_channel: typing.Optional[commands.TextChannelConverter] = None,
    ):
        """
        If enabled then it checks against any scam, phishing or adult links which is posted by members and take actions accordingly

        Args:
            - option : It accepts the following options ; True, False, yes, no, on, off
            - action [Optional] (default: log) : What kind of action to take, It accepts the following options ; 'ban', 'mute', 'timeout', 'kick', 'log'
            - logging_channel [Optional] : It will log in a specific channel if specified, otherwise it will log the message where the link was sent. Default

        `Note: If 'log' action is selected then, I will only delete the message and log it the current channel where the link was sent and will do nothing`
        """
        await self.add_and_check_data(
            dict_to_add={
                "badlinks": {
                    "option": option,
                    "action": action,
                    "logging_channel": logging_channel,
                }
            },
            ctx=ctx,
        )

    @commands.command()
    @commands.guild_only()
    @is_mod()
    async def raw_data(self, ctx):
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
                ))
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
                ))
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
                ))
            embeds_list.append(embed)

        paginator = EmbedPaginator(entries=embeds_list, ctx=ctx)
        await paginator.start()


def setup(bot):
    bot.add_cog(ServerSetup(bot))
