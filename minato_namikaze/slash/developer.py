from __future__ import annotations

import json
import logging
import os
import typing
from typing import List

import aiohttp
import discord
from DiscordUtils import ErrorEmbed
from DiscordUtils import StarboardEmbed
from DiscordUtils import SuccessEmbed
from lib import BASE_DIR
from lib import Database
from lib import LinksAndVars
from lib import Webhooks

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


class FeedbackModal(discord.ui.Modal):
    children: list[discord.ui.InputText]

    def __init__(self):
        children: list[discord.ui.Item] = [
            discord.ui.InputText(
                label="Your suggestion(s)/feedback or report",
                style=discord.InputTextStyle.paragraph,
                required=True,
                min_length=20,
                placeholder="Type in your suggestions/feedback or report",
            ),
        ]

        super().__init__(title="Feedback / Suggestions / Report", children=children)

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = StarboardEmbed(
            title="Feedback / Suggestions / Report",
            description=self.children[0].value,
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text=f"{interaction.guild.name} [{interaction.guild_id}]")
        embed.timestamp = discord.utils.utcnow()
        async with aiohttp.ClientSession() as session:
            wh = discord.Webhook.from_url(Webhooks.feedback.value, session=session)
            await wh.send(embed=embed)
        await interaction.response.send_message(
            "Your message was successfully sent to my developer",
            ephemeral=True,
        )


class Feedback(discord.SlashCommand):
    """Send feedback, suggestion or report regarding me to my developer"""

    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        await response.send_modal(FeedbackModal())


class Blacklist(discord.SlashCommand):
    """Some blacklist releated secret commands"""

    def __init__(self, cog):
        self.cog = cog

    async def command_check(self, response: discord.SlashCommandResponse):
        if await self.cog.bot.is_owner(response.user):
            return True
        else:
            await response.send_message(
                "Sorry! but only developer can use this",
                ephemeral=True,
            )
            return False


class User(discord.SlashCommand, parent=Blacklist):
    """Adds user to the blacklist"""

    id: str = discord.application_command_option(
        description="The user to add to the blacklist",
        default=None,
    )
    reason: str | None = discord.application_command_option(
        description="Reason",
        default=None,
    )

    async def callback(self, response: discord.SlashCommandResponse) -> None:
        user_id = response.options.id
        if not str(user_id).isdigit():
            return await response.send_message("Not a valid userid", ephemeral=True)
        if self.parent.cog.bot.get_user(int(user_id)):
            database = await self.parent.cog.database_class_user()
            await database.set(user_id, response.options.reason)
            self.parent.cog.bot.blacklist.append(int(user_id))
            await response.send_message("User added to the blacklist", ephemeral=True)
            return
        else:
            await response.send_message("User not found", ephemeral=True)


class Server(discord.SlashCommand, parent=Blacklist):
    """Adds guild to the blacklist"""

    id: str = discord.application_command_option(
        description="The server which is to be added",
        default=None,
    )
    reason: str | None = discord.application_command_option(
        description="Reason",
        default=None,
    )

    async def callback(self, response: discord.SlashCommandResponse) -> None:
        server_id = response.options.id or response.guild_id
        if not str(server_id).isdigit():
            return await response.send_message("Not a valid serverid", ephemeral=True)
        guild = self.parent.cog.bot.get_guild(int(server_id))
        if guild is not None:
            database = await self.parent.cog.database_class_server()
            await database.set(server_id, response.options.reason)
            self.parent.cog.bot.blacklist.append(int(server_id))
            channel = await self.parent.cog.bot.get_welcome_channel(guild)
            embed = ErrorEmbed(title=f"Left {guild.name}")
            embed.description = f"I have to leave the `{guild.name}` because it was marked as a `blacklist guild` by my developer. For further queries please contact my developer."
            embed.add_field(
                name="Developer",
                value=f"[{self.parent.cog.bot.get_user(self.parent.cog.bot.owner_id)}](https://discord.com/users/{self.parent.cog.bot.owner_id})",
            )
            embed.add_field(
                name="Support Server",
                value=f"https://discord.gg/{LinksAndVars.invite_code.value}",
            )
            await channel.send(embed=embed)
            await guild.leave()
            log.info(f"Left guild {guild.id} [Marked as spam]")
            await response.send_message("Server added to the blacklist", ephemeral=True)
            return
        else:
            return await response.send_message("Server not found", ephemeral=True)


class Fetch(discord.SlashCommand, parent=Blacklist):
    """Fetches data from the blacklist list of users and server"""

    id: str = discord.application_command_option(
        description="The server/user data which is to be fetched",
        default=None,
    )

    async def callback(self, response: discord.SlashCommandResponse) -> None:
        database_user = await self.parent.cog.database_class_user()
        database_server = await self.parent.cog.database_class_server()
        user_check = await database_user.get(response.options.id)
        server_check = await database_server.get(response.options.id)
        if user_check is None and server_check is None:
            return await response.send_message(
                embed=ErrorEmbed(title="No data found"),
                ephemeral=True,
            )
        return await response.send_message(
            embed=SuccessEmbed(
                title=response.options.id,
                description=f"Found in {database_user._Database__channel.mention if user_check is not None else database_server._Database__channel.mention}\n\n **Reason**\n```\n{user_check or server_check}\n```",
            ),
        )


class Delete(discord.SlashCommand, parent=Blacklist):
    """Delete the data if found blacklist list"""

    id: str = discord.application_command_option(
        description="The server/user data which is to be fetched",
        default=None,
    )

    async def callback(self, response: discord.SlashCommandResponse) -> None:
        if not str(response.options.id).isdigit():
            return await response.send_message(
                "Not a valid serverid/userid",
                ephemeral=True,
            )
        await response.send_message(
            "If data is available then will be removed from the blacklist",
            ephemeral=True,
        )
        database_user = await self.parent.cog.database_class_user()
        database_server = await self.parent.cog.database_class_server()
        await database_user.delete(response.options.id)
        await database_server.delete(response.options.id)

        try:
            self.parent.cog.bot.blacklist.remove(int(response.options.id))
        except ValueError:
            pass


class Commands(
    discord.SlashCommand,
    global_command=False,
    guild_ids=[920536143244709889, 920190307595874304],
):
    """Some bot commands releated secret commands"""

    def __init__(self, cog):
        self.cog = cog
        # if not cog.bot.local:
        #     self.disabled = True

    async def command_check(self, response: discord.SlashCommandResponse):
        if await self.cog.bot.is_owner(response.user):
            return True
        else:
            await response.send_message(
                "Sorry! but only developer can use this",
                ephemeral=True,
            )
            return False

    async def callback(self, response: discord.SlashCommandResponse) -> None:
        await response.send_message("Will be soon updated", ephemeral=True)
        json_to_be_given = {}
        for cog_name in self.cog.bot.cogs:
            cog = self.cog.bot.cogs[cog_name]
            cog_commands_list = []
            for command in cog.walk_commands():
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
                        command_dict.update({"description": command.description})
                    if command.clean_params or len(command.params) != 0:
                        command_dict.update({"params": list(command.clean_params)})
                    if command.full_parent_name is not None:
                        command_dict.update({"parent": command.full_parent_name})
                    cog_commands_list.append(command_dict)
            if len(cog_commands_list) != 0:
                json_to_be_given.update(
                    {
                        str(cog_name): {
                            "cog_commands_list": cog_commands_list,
                            "description": cog.description,
                        },
                    },
                )
        application_commands = []
        for i in self.cog.bot.application_commands:
            app_command_dict = {"name": i.name, "description": i.description}
            options = []
            for j in i.options:
                options.append(
                    {
                        "name": j.name,
                        "description": j.description,
                        "required": j.required,
                        "type": j.type.name,
                    },
                )
            app_command_dict.update({"options": options})
            application_commands.append(app_command_dict)
        with open(BASE_DIR / os.path.join("lib", "data", "commands.json"), "w") as f:
            json.dump(
                {
                    "commands": json_to_be_given,
                    "application_commands": application_commands,
                },
                f,
            )


class DeveloperCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Feedback(self))
        self.add_application_command(Blacklist(self))
        self.add_application_command(Commands(self))

    async def database_class_user(self):
        return await self.bot.db.new(
            Database.database_category_name.value,
            Database.user_blacklist_channel_name.value,
        )

    async def database_class_server(self):
        return await self.bot.db.new(
            Database.database_category_name.value,
            Database.server_blacklist_channel_name.value,
        )


def setup(bot):
    bot.add_cog(DeveloperCog(bot))
