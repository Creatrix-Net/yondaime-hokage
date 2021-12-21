from __future__ import annotations

import asyncio
import io
from typing import Optional, Union

import discord
from discord.ext import commands

from .vars import ChannelAndMessageId, SetupVars


class ConfirmationView(discord.ui.View):
    def __init__(
        self,
        *,
        timeout: float,
        author_id: int,
        reacquire: bool,
        ctx: Context,
        delete_after: bool,
    ) -> None:
        super().__init__(timeout=timeout)
        self.value: Optional[bool] = None
        self.delete_after: bool = delete_after
        self.author_id: int = author_id
        self.ctx: Context = ctx
        self.reacquire: bool = reacquire
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id == self.author_id:
            return True
        else:
            await interaction.response.send_message(
                "This confirmation dialog is not for you.", ephemeral=True
            )
            return False

    async def on_timeout(self) -> None:
        if self.reacquire:
            await self.ctx.acquire()
        if self.delete_after and self.message:
            await self.message.delete()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_message()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        await interaction.response.defer()
        if self.delete_after:
            await interaction.delete_original_message()
        self.stop()


class Context(commands.Context):
    async def entry_to_code(self, entries):
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"{name:<{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    async def indented_entry_to_code(self, entries):
        width = max(len(a) for a, b in entries)
        output = ["```"]
        for name, entry in entries:
            output.append(f"\u200b{name:>{width}}: {entry}")
        output.append("```")
        await self.send("\n".join(output))

    def __repr__(self):
        # we need this for our cache key strategy
        return "<Context>"

    @property
    def session(self):
        return self.bot.session

    @discord.utils.cached_property
    def replied_reference(self):
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    async def prompt(
        self,
        message: str,
        *,
        timeout: float = 60.0,
        delete_after: bool = True,
        reacquire: bool = True,
        author_id: Optional[int] = None,
    ) -> Optional[bool]:
        """An interactive reaction confirmation dialog.
        Parameters
        -----------
        message: str
            The message to show along with the prompt.
        timeout: float
            How long to wait before returning.
        delete_after: bool
            Whether to delete the confirmation message after we're done.
        reacquire: bool
            Whether to release the database connection and then acquire it
            again when we're done.
        author_id: Optional[int]
            The member who should respond to the prompt. Defaults to the author of the
            Context's message.
        Returns
        --------
        Optional[bool]
            ``True`` if explicit confirm,
            ``False`` if explicit deny,
            ``None`` if deny due to timeout
        """

        author_id = author_id or self.author.id
        view = ConfirmationView(
            timeout=timeout,
            delete_after=delete_after,
            reacquire=reacquire,
            ctx=self,
            author_id=author_id,
        )
        view.message = await self.send(message, view=view)
        await view.wait()
        return view.value

    def tick(self, opt, label=None):
        lookup = {
            True: "<:greenTick:330090705336664065>",
            False: "<:redTick:330090723011592193>",
            None: "<:greyTick:563231201280917524>",
        }
        emoji = lookup.get(opt, "<:redTick:330090723011592193>")
        if label is not None:
            return f"{emoji}: {label}"
        return emoji

    async def show_help(self, command=None):
        """Shows the help command for the specified command if given.
        If no command is given, then it'll show help for the current
        command.
        """
        cmd = self.bot.get_command("help")
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)

    async def safe_send(self, content, *, escape_mentions=True, **kwargs):
        """Same as send except with some safe guards.
        1) If the message is too long then it sends a file with the results instead.
        2) If ``escape_mentions`` is ``True`` then it escapes mentions.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = io.BytesIO(content.encode())
            kwargs.pop("file", None)
            return await self.send(
                file=discord.File(fp, filename="message_too_long.txt"), **kwargs
            )
        else:
            return await self.send(content)

    def return_ban_channel(self, guild: Optional[discord.Guild]):
        guild = guild or self.guild
        return discord.utils.get(
            self.guild.text_channels if self else guild.text_channels,
            topic=SetupVars.ban.value,
        )

    def return_unban_channel(self, guild: Optional[discord.Guild]):
        guild = guild or self.guild
        return discord.utils.get(
            self.guild.text_channels if self else guild.text_channels,
            topic=SetupVars.unban.value,
        )

    def return_feedback_channel(self, guild: Optional[discord.Guild]):
        guild = guild or self.guild
        return discord.utils.get(
            self.guild.text_channels if self else guild.text_channels,
            topic=SetupVars.feedback.value,
        )

    def return_support_channel(self, guild: Optional[discord.Guild]):
        guild = guild or self.guild
        return discord.utils.get(
            self.guild.text_channels if self else guild.text_channels,
            topic=SetupVars.support.value,
        )

    def return_warning_channel(self, guild: Optional[discord.Guild]):
        guild = guild or self.guild
        return discord.utils.get(
            self.guild.text_channels if self else guild.text_channels,
            topic=SetupVars.warns.value,
        )

    def get_user(self, user: Union[int, discord.Member]):
        if isinstance(user, int):
            user = self.bot.get_user(user)
        return user

    async def get_dm(self, user: Union[int, discord.Member]):
        try:
            if isinstance(user, int):
                user = self.bot.get_or_fetch_member(user, self.guild)
            else:
                user = self.bot.get_or_fetch_member(user.id, self.guild)
        except:
            if isinstance(user, int):
                user = ctx.bot.get_user(user)
        return user.dm_channel if user.dm_channel else await user.create_dm()

    def get_roles(self, role: Union[int, discord.Role]):
        if isinstance(role, int):
            role = discord.utils.get(self.guild.roles, id=role)
        return role

    def get_emoji(self, emoji: Union[int, discord.Emoji, discord.PartialEmoji]):
        if isinstance(emoji, int):
            emoji = discord.utils.get(self.guild.emojis, id=role)
        return emoji

    def get_guild(self, guild: Union[int, discord.Guild, discord.PartialInviteGuild]):
        if isinstance(guild, int):
            guild = self.bot.get_guild(guild)
        return guild

    def get_config_emoji_by_name_or_id(self, emoji: Union[int, str]):
        if isinstance(emoji, str):
            guild1 = self.get_guild(ChannelAndMessageId.server_id.value)
            emoji_model = discord.utils.get(guild1.emojis, name=emoji)
            if not emoji:
                guild2 = self.get_guild(ChannelAndMessageId.server_id2.value)
                emoji_model = discord.utils.get(guild2.emojis, name=emoji)
            return emoji_model
        else:
            return self.bot.get_emoji(emoji)

    def get_config_channel_by_name_or_id(self, channel: Union[int, str]):
        if isinstance(channel, str):
            guild1 = self.get_guild(ChannelAndMessageId.server_id.value)
            channel_model = discord.utils.get(
                guild1.text_channels, name=channel)
            if not channel:
                guild2 = self.get_guild(ChannelAndMessageId.server_id2.value)
                channel_model = discord.utils.get(
                    guild2.text_channels, name=channel)
            return channel_model
        else:
            return self.bot.get_channel(channel)
