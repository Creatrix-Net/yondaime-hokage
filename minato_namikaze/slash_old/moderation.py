from __future__ import annotations

import random
import typing
from datetime import timedelta

import aiohttp
import discord
from discord.abc import GuildChannel
from DiscordUtils import ErrorEmbed
from DiscordUtils import SuccessEmbed
from lib import Database
from lib import detect_bad_domains
from lib import LinksAndVars
from lib import RaidMode


class Badurls(discord.SlashCommand, name="badurls"):
    """Check if a text has a malicious url or not from a extensive list 60k+ flagged domains"""

    name = "bad urls"

    content = discord.application_command_option(
        description="The text, url or a list of urls to check",
        type=str,
    )

    @content.autocomplete
    async def content_autocomplete(
        self,
        response: discord.AutocompleteResponse,
    ) -> typing.AsyncIterator[str]:
        async with aiohttp.ClientSession() as session, session.get(
            LinksAndVars.bad_links.value,
        ) as resp:
            list_of_bad_domains = (await resp.text()).split("\n")

        end = random.randint(25, len(list_of_bad_domains))
        for domain in list_of_bad_domains[end - 25 : end]:
            if response.value.lower() in domain.lower():
                yield domain

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        detected_urls = await detect_bad_domains(response.options.content)
        if len(detected_urls) != 0:
            embed = ErrorEmbed(title="SCAM/PHISHING/ADULT LINK(S) DETECTED")
            detected_string = "\n".join([f"- ||{i}||" for i in set(detected_urls)])
            embed.description = (
                f"The following scam url(s) were detected:\n{detected_string}"
            )
            embed.set_author(
                name=response.interaction.user.display_name,
                icon_url=response.interaction.user.display_avatar.url,
            )
            await response.send_message(embed=embed, ephemeral=True)
            return
        await response.send_message(
            embed=SuccessEmbed(title="The url or the text message is safe!"),
            ephemeral=True,
        )


class BadurlsMessageCommand(discord.MessageCommand, name="Flagged Urls"):
    """Check if a text has a malicious url or not from a extensive list 60k+ flagged domains"""

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.MessageCommandResponse):
        message = response.target
        detected_urls = await detect_bad_domains(message.content)
        if len(detected_urls) != 0:
            embed = ErrorEmbed(title="SCAM/PHISHING/ADULT LINK(S) DETECTED")
            detected_string = "\n".join([f"- ||{i}||" for i in set(detected_urls)])
            embed.description = (
                f"The following scam url(s) were detected:\n{detected_string}"
            )
            embed.set_author(
                name=response.target.author.display_name,
                icon_url=response.target.author.display_avatar.url,
            )
            await response.send_message(embed=embed, ephemeral=True)
            return
        await response.send_message(
            embed=SuccessEmbed(title="The url or the text message is safe!"),
            ephemeral=True,
        )


class AntiRaid(discord.SlashCommand):
    """Enable or disable Antiraid system for the server"""

    switch: typing.Literal["on", "strict", "off"] = discord.application_command_option(
        description="Antiraid different modes",
        default="on",
    )
    channel: GuildChannel = discord.application_command_option(
        channel_types=[discord.TextChannel],
        description="Channel to broadcast join messages",
    )

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).manage_guild:
            return True
        else:
            await response.send_message(
                "You don't have the `Manage Guild` permission",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.SlashCommandResponse):
        database = await self.cog.bot.db.new(
            Database.database_category_name.value,
            Database.antiraid_channel_name.value,
        )
        switch = response.options.switch
        if switch.lower() == "off":
            await database.delete(response.interaction.guild_id)
            try:
                await response.interaction.guild.edit(
                    verification_level=discord.VerificationLevel.low,
                )
                await response.send_message(
                    "Raid mode disabled. No longer broadcasting join messages.",
                    ephemeral=True,
                )
            except discord.HTTPException:
                await response.send_message(
                    "\N{WARNING SIGN} Could not set verification level.",
                    ephemeral=True,
                )
            return
        if switch.lower() == "strict":
            try:
                await response.interaction.guild.edit(
                    verification_level=discord.VerificationLevel.high,
                )
                update_dict = {
                    "raid_mode": RaidMode.strict.value,
                    "broadcast_channel": response.options.channel.id,
                }
                await self.cog.add_and_check_data(
                    update_dict,
                    response.interaction.guild,
                    "antiraid",
                )
                await response.send_message(
                    f"Raid mode enabled. Broadcasting join messages to {response.options.channel.mention}.",
                    ephemeral=True,
                )
            except discord.HTTPException:
                await response.send_message(
                    "\N{WARNING SIGN} Could not set verification level.",
                    ephemeral=True,
                )
            return
        try:
            await response.interaction.guild.edit(
                verification_level=discord.VerificationLevel.medium,
            )
            update_dict = {
                "raid_mode": RaidMode.on.value,
                "broadcast_channel": response.options.channel.id,
            }
            await self.cog.add_and_check_data(
                update_dict,
                response.interaction.guild,
                "antiraid",
            )
            await response.send_message(
                f"Raid mode enabled. Broadcasting join messages to {response.options.channel.mention}.",
                ephemeral=True,
            )
        except discord.HTTPException:
            await response.send_message(
                "\N{WARNING SIGN} Could not set verification level.",
                ephemeral=True,
            )


class Kick(discord.UserCommand):
    """Kicks the user from guild"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).kick_members:
            return True
        else:
            await response.send_message(
                "You don't have the `Kick Members` permission",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.kick(
                reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})",
            )
            await response.send_message(f"{user} kicked :foot:", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException):
            await response.send_message(
                "Something went wrong or I don't have the `Kick Members` permission",
                ephemeral=True,
            )


class Ban(discord.UserCommand):
    """Bans the user from guild"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).ban_members:
            return True
        else:
            await response.send_message(
                "You don't have the `Ban Members` permission",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.ban(
                reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})",
            )
            await response.send_message(f"{user} banned :hammer:", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException):
            await response.send_message(
                "Something went wrong or I don't have the `Ban Members` permission",
                ephemeral=True,
            )


class Mute(discord.UserCommand):
    """Mute the user from guild for a day"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).timeout_members:
            return True
        else:
            await response.send_message(
                "You don't have the `Timeout Members` permission",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.edit(
                timed_out_until=discord.utils.utcnow() + timedelta(days=1),
                reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})",
            )
            await response.send_message(f"{user} muted for a day :x:", ephemeral=True)
        except (discord.Forbidden, discord.HTTPException):
            await response.send_message(
                "Something went wrong or I don't have the `Timeout Members` permission",
                ephemeral=True,
            )


class Unmute(discord.UserCommand):
    """Unmute the user from guild"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).timeout_members:
            return True
        else:
            await response.send_message(
                "You don't have the `Timeout Members` permission",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.edit(
                timed_out_until=discord.utils.utcnow(),
                reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})",
            )
            await response.send_message(
                f"{user} unmuted :white_check_mark:",
                ephemeral=True,
            )
        except (discord.Forbidden, discord.HTTPException):
            await response.send_message(
                "Something went wrong or I don't have the `Timeout Members` permission",
                ephemeral=True,
            )


class Setup(discord.SlashCommand):
    """Setups some logging system for system for server with some nice features"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).manage_guild:
            return True
        else:
            await response.send_message(
                "You don't have the `Manage Guild` permission",
                ephemeral=True,
            )
            return False


class Add(discord.SlashCommand, parent=Setup):
    """This adds logging of the some things in the specified text channel"""

    add_type: typing.Literal[
        "ban",
        "feedback",
        "warns",
        "unban",
    ] = discord.application_command_option(
        description="which to log",
        name="type",
        default=None,
    )
    channel: GuildChannel = discord.application_command_option(
        channel_types=[discord.TextChannel],
        description="The logging channel",
    )

    async def callback(self, response: discord.SlashCommandResponse):
        dict_to_add = {str(response.options.type): response.options.channel.id}
        await self.parent.cog.add_and_check_data(
            dict_to_add,
            response.interaction.guild,
            "setupvar",
        )
        await response.send_message(
            f"Done! `Added {response.options.type} logging` to {response.options.channel.mention}",
        )


class Support(discord.SlashCommand, parent=Setup):
    """This adds support system to your server"""

    channel: GuildChannel = discord.application_command_option(
        channel_types=[discord.TextChannel],
        description="The support logging channel",
    )
    role: discord.Role = discord.application_command_option(
        description="The role using which memebrs can access that support channel",
    )

    async def callback(self, response: discord.SlashCommandResponse):
        dict_to_add = {
            "support": [response.options.channel.id, response.options.role.id],
        }
        await self.parent.cog.add_and_check_data(
            dict_to_add,
            response.interaction.guild,
            "setupvar",
        )
        await response.send_message(
            f"Done! Added `support logging` to {response.options.channel.mention} with {response.options.role.mention} `role`",
        )


class Starboard(discord.SlashCommand, parent=Setup):
    """This adds starboard system to your server"""

    channel: GuildChannel = discord.application_command_option(
        channel_types=[discord.TextChannel],
        description="The channel where the starred message will go",
    )
    stars: int | None = discord.application_command_option(
        description="Minimum number of stars required before posting it to the specified channel",
        default=5,
    )
    self_star: bool | None = discord.application_command_option(
        description="Whether self  starring of message should be there or not",
        default=False,
    )
    ignore_nsfw: bool | None = discord.application_command_option(
        description="Whether to ignore NSFW channels or not",
        default=True,
    )

    async def callback(self, response: discord.SlashCommandResponse):
        dict_to_add = {
            "starboard": {
                "channel": response.options.channel.id,
                "no_of_stars": response.options.stars,
                "self_star": response.options.self_star,
                "ignore_nsfw": response.options.ignore_nsfw,
            },
        }
        await self.parent.cog.add_and_check_data(
            dict_to_add,
            response.interaction.guild,
            "setupvar",
        )
        await response.send_message(
            f"Done! Added `starboard channel` as {response.options.channel.mention} with minimum `{response.options.stars} stars` requirement",
        )


class BadLinks(discord.SlashCommand, parent=Setup):
    """Checks against the scam links and take necessary action if stated"""

    option: bool = discord.application_command_option(
        description="Enable or Disable",
        default=True,
    )
    action: None | (typing.Literal["ban", "mute", "timeout", "kick", "log"]) = (
        discord.application_command_option(
            description="What kind of action to take",
            default=None,
        )
    )
    channel: GuildChannel | None = discord.application_command_option(
        channel_types=[discord.TextChannel],
        description="Log channel",
        default=None,
    )

    async def callback(self, response: discord.SlashCommandResponse):
        if not response.options.option:
            database = await self.parent.cog.database_class()
            guild_dict = await database.get(response.interaction.guild.id)
            if guild_dict is None:
                return
            guild_dict.pop("badlinks")
            await database.set(response.interaction.guild.id, guild_dict)
            await response.send_message("Badlink system turned off!")
            return
        await self.parent.cog.add_and_check_data(
            {
                "badlinks": {
                    "option": response.options.option,
                    "action": response.options.action,
                    "logging_channel": (
                        response.options.channel.id
                        if response.options.channel is not None
                        else response.options.channel
                    ),
                },
            },
            response.interaction.guild,
            "setupvar",
        )
        await response.send_message(
            f"Done! If I detect any scam link then I `delete` that and will do a `{response.options.action}` action",
        )


class ModerationCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Badurls(self))
        self.add_application_command(BadurlsMessageCommand(self))
        self.add_application_command(AntiRaid(self))
        self.add_application_command(Kick(self))
        self.add_application_command(Ban(self))
        self.add_application_command(Mute(self))
        self.add_application_command(Unmute(self))
        self.add_application_command(Setup(self))

    async def database_class(self):
        return await self.bot.db.new(
            Database.database_category_name.value,
            Database.database_channel_name.value,
        )

    async def database_class_antiraid(self):
        return await self.bot.db.new(
            Database.database_category_name.value,
            Database.antiraid_channel_name.value,
        )

    async def database_class_mentionspam(self):
        return await self.bot.db.new(
            Database.database_category_name.value,
            Database.mentionspam_channel_name.value,
        )

    async def add_and_check_data(
        self,
        dict_to_add: dict,
        guild: discord.Guild,
        type_store: typing.Literal["antiraid", "setupvar", "mentionspam"],
    ) -> None:
        if type_store == "antiraid":
            database = await self.database_class_antiraid()
        if type_store == "setupvar":
            database = await self.database_class()
        if type_store == "mentionspam":
            database = await self.database_class_mentionspam()
        guild_dict = await database.get(guild.id)
        if guild_dict is None:
            await database.set(guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await database.set(guild.id, guild_dict)
        return


def setup(bot):
    bot.add_cog(ModerationCog(bot))
