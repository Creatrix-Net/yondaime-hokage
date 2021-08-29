from random import randint
from typing import List, Union

import discord
from discord.channel import _single_delete_strategy
from discord.ext import commands
from discord.ext.commands.help import HelpCommand

from .menu import DefaultMenu


class SelectedHelp(HelpCommand):
    def __init__(self, **options):
        self.color = options.pop(
            "color",
            discord.Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255)),
        )
        self.dm_help = options.pop("dm_help", False)
        self.index_title = options.pop("index_title", "Categories")
        self.no_category = options.pop("no_category", "No Category")
        self.sort_commands = options.pop("sort_commands", True)
        self.menu = options.pop("menu", DefaultMenu())
        self.ending_note = options.pop("ending_note", "")

        super().__init__(**options)

    async def prepare_help_command(
        self, ctx: commands.Context, command: commands.Command
    ):
        if ctx.guild is not None:
            perms = ctx.channel.permissions_for(ctx.guild.me)
            if not perms.embed_links:
                raise commands.BotMissingPermissions(("embed links",))
            if not perms.read_message_history:
                raise commands.BotMissingPermissions(("read message history",))

        await super().prepare_help_command(ctx, command)

    def get_ending_note(self):
        """Returns help command's ending note. This is mainly useful to override for i18n purposes."""
        note = self.ending_note or (
            "Type {help.clean_prefix}{help.invoked_with} command for more info on a command.\n"
            "You can also type {help.clean_prefix}{help.invoked_with} category for more info on a category."
        )
        return note.format(ctx=self.context, help=self)

    async def send_pages(self):
        pages = self.paginator.pages
        destination = self.get_destination()
        if not pages:
            await destination.send(f"```{self.get_ending_note()}```")
        else:
            await self.menu.send_pages(self.context, destination, pages)

    def get_destination(self):
        ctx = self.context
        if self.dm_help is True:
            return ctx.author
        else:
            return ctx.channel

    async def send_bot_help(self, mapping: dict):
        bot = self.context.bot
        channel = self.get_destination()
        async with channel.typing():
            mapping = []
            help_filtered = (
                filter(lambda c: c.name != "help", bot.commands)
                if len(bot.commands) > 1
                else bot.commands
            )
            for cmd in await self.filter_commands(help_filtered, sort=self.sort_commands,):
                mapping.append(cmd.cog.qualified_name)
            mapping = list(set(mapping))
            mapping.sort()
        await self.send_pages()

    async def send_command_help(self, command: commands.Command):
        filtered = await self.filter_commands([command])
        if filtered:
            self.paginator.add_command(command, self.get_command_signature(command))
            await self.send_pages()

    async def send_group_help(self, group: commands.Group):
        async with self.get_destination().typing():
            filtered = await self.filter_commands(
                group.commands, sort=self.sort_commands
            )
            # if filtered:
            self.paginator.add_group(group, filtered)
        await self.send_pages()

    async def send_cog_help(self, cog: commands.Cog):
        async with self.get_destination().typing():
            filtered = await self.filter_commands(
                cog.get_commands(), sort=self.sort_commands
            )
            self.paginator.add_cog(cog, filtered)
        await self.send_pages()