import asyncio
from typing import List, Union

import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from pretty_help.pretty_help import Paginator

from ..classes import Embed
from ..functions import emoji_random_func
from ..util import help_smile_emoji, server_id
from .buttons_class import SupportServerButton, Google

class CustomHelpPaginator(Paginator):
    def add_cog(
        self, title: Union[str, commands.Cog], commands_list: List[commands.Command],bot=None
    ):
        cog = isinstance(title, commands.Cog)
        if not commands_list:
            return

        page_title = title.qualified_name if cog else title
        if bot:
            page_title += ' ' + emoji_random_func(bot)
        embed = self._new_page(
            page_title, (title.description or "") if cog else "")
        self._add_command_fields(embed, page_title, commands_list)

    def add_command(self, command: commands.Command, signature: str, bot=None):
        desc = f"{command.description}\n\n" if command.description else ""
        page = self._new_page(
            command.qualified_name + ' ' +
            emoji_random_func(bot) if bot else command.qualified_name,
            f"{self.prefix}{self.__command_info(command)}{self.suffix}" or "",
        )
        if command.aliases:
            aliases = ", ".join(command.aliases)
            page.add_field(
                name="**Aliases**",
                value=f"{self.prefix}{aliases}{self.suffix}",
                inline=False,
            )
        page.add_field(
            name="**Usage**", value=f"{self.prefix}{signature}{self.suffix}", inline=False
        )
        self._add_page(page)


class MenuHelp(DefaultMenu):
    async def send_pages(
        self,
        ctx: commands.Context,
        destination: discord.abc.Messageable,
        pages: List[discord.Embed],
    ):
        total = len(pages)
        message: discord.Message = await destination.send(embed=pages[0], view=Google())

        if total > 1:
            bot: commands.Bot = ctx.bot
            navigating = True
            index = 0

            for reaction in self:
                await message.add_reaction(reaction)

            while navigating:
                try:

                    def check(payload: discord.RawReactionActionEvent):

                        if (
                            payload.user_id != bot.user.id
                            and message.id == payload.message_id
                        ):
                            return True

                    payload: discord.RawReactionActionEvent = await bot.wait_for(
                        "raw_reaction_add", timeout=self.active_time, check=check
                    )

                    emoji_name = (
                        payload.emoji.name
                        if payload.emoji.id is None
                        else f":{payload.emoji.name}:{payload.emoji.id}"
                    )

                    if emoji_name in self and payload.user_id == ctx.author.id:
                        nav = self.get(emoji_name)
                        if not nav:

                            navigating = False
                            return await message.delete()
                        else:
                            index += nav
                            embed: discord.Embed = pages[index % total]

                            await message.edit(embed=embed)

                    try:
                        await message.remove_reaction(
                            payload.emoji, discord.Object(id=payload.user_id)
                        )
                    except discord.errors.Forbidden:
                        pass

                except asyncio.TimeoutError:
                    navigating = False
                    for emoji in self:
                        try:
                            await message.remove_reaction(emoji, bot.user)
                        except Exception:
                            pass


class HelpClassPretty(PrettyHelp):
    def __init__(self, **options):
        super().__init__(**options)
        self.paginator = CustomHelpPaginator(
            color=self.color, show_index=options.pop("show_index", True)
        )
    
    def get_ending_note(self):
        """Returns help command's ending note. This is mainly useful to override for i18n purposes."""
        note = self.ending_note or (
            "Type {help.invoked_with} command for more info on a command.\n"
            "You can also type {help.invoked_with} category for more info on a category."
        )
        return note.format(ctx=self.context, help=self)
    
    async def send_bot_help(self, mapping: dict):
        bot = self.context.bot
        channel = self.get_destination()
        async with channel.typing():
            mapping = dict((name, []) for name in mapping)
            help_filtered = (
                filter(lambda c: c.name != "help", bot.commands)
                if len(bot.commands) > 1
                else bot.commands
            )
            for cmd in await self.filter_commands(
                help_filtered, sort=self.sort_commands,
            ):
                mapping[cmd.cog].append(cmd)
            self.paginator.add_cog(self.no_category, mapping.pop(None), bot=self.context.bot)
            sorted_map = sorted(
                mapping.items(),
                key=lambda cg: cg[0].qualified_name
                if isinstance(cg[0], commands.Cog)
                else str(cg[0]),
            )
            for cog, command_list in sorted_map:
                self.paginator.add_cog(cog, command_list, bot)
            self.paginator.add_index(f'self.index_title {emoji_random_func(bot)}', bot)
        await self.send_pages()