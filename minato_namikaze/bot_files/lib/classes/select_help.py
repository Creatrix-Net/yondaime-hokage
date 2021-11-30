"""
This code has been fully copied from here https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/paginator.py
"""
from __future__ import annotations

import inspect
from itertools import islice

import discord
from discord.ext import commands, menus

from ..util import LinksAndVars
from .paginator import *
from .time_class import *

DEFAULT_COMMAND_SELECT_LENGTH=20

def chunks(data, SIZE: int = DEFAULT_COMMAND_SELECT_LENGTH):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

class GroupHelpPageSource(menus.ListPageSource):
    def __init__(
        self,
        group: Union[commands.Group, commands.Cog],
        commands: List[commands.Command],
        *,
        prefix: str,
    ):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f"{self.group.qualified_name} Commands"
        self.description = self.group.description[:100]

    async def format_page(self, menu, commands):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            colour=discord.Colour.random(),
        )

        for command in commands:
            signature = f"{command.qualified_name} {command.signature}"
            embed.add_field(
                name=signature,
                value=command.short_doc or "No help given...",
                inline=False,
            )

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(
                name=f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)"
            )

        embed.set_footer(
            text=f'Use "{self.prefix}help command" for more info on a command.'
        )
        return embed


class HelpSelectMenu(discord.ui.Select["HelpMenu"]):
    def __init__(
        self,
        commands: Dict[commands.Cog, List[commands.Command]],
        bot: commands.AutoShardedBot,
        add_index: bool = True
    ):
        super().__init__(
            placeholder="Select a category...",
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands = commands
        self.bot = bot
        self.add_index = add_index
        self.__fill_options()

    def __fill_options(self) -> None:
        if self.add_index:
            self.add_option(
                label="Index",
                emoji="\N{WAVING HAND SIGN}",
                value="__index",
                description="The help page showing how to use the bot.",
            )
        for cog, cog_commands in self.commands.items():
            if not cog_commands:
                continue
            description = cog.description.split("\n", 1)[0] or None
            emoji = getattr(cog, "display_emoji", None)
            self.add_option(
                label=cog.qualified_name,
                value=cog.qualified_name,
                description=description,
                emoji=emoji,
            )

    async def callback(self, interaction: discord.Interaction):
        if self.view is None:
            raise AssertionError
        value = self.values[0]
        if value == "__index":
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message(
                    "Somehow this category does not exist?", ephemeral=True)
                return

            commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message(
                    "This category has no commands for you", ephemeral=True)
                return

            source = GroupHelpPageSource(cog,
                                         commands,
                                         prefix=self.view.ctx.clean_prefix)
            await self.view.rebind(source, interaction)


class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        # This forces the buttons to appear even in the front page
        return True

    def get_max_pages(self) -> Optional[int]:
        # There's only one actual page in the front page
        # However we need at least 2 to show all the buttons
        return 2

    async def get_page(self, page_number: int) -> Any:
        # The front page is a dummy
        self.index = page_number
        return self

    def format_page(self, menu: HelpMenu, page):
        embed = discord.Embed(title="Bot Help",
                              colour=discord.Colour(0xA8B9CD))
        embed.description = inspect.cleandoc(f"""
            Hello! Welcome to the help page.

            Use "{menu.ctx.clean_prefix}help command" for more info on a command.
            Use "{menu.ctx.clean_prefix}help category" for more info on a category.
            Use the dropdown menu below to select a category.
        """)

        embed.add_field(
            name="Support Server",
            value="For more help, consider joining the official server over at https://discord.gg/S8kzbBVN8b",
            inline=False,
        )

        created_at = format_dt(menu.ctx.bot.user.created_at, "F")
        if self.index == 0:
            embed.add_field(
                name="Who are you?",
                value=(":pray: Konichiwa :pray:, myself **Minato Namikaze**, **Konohagakure <:uzumaki_naruto:874930645405675521> Yondaime Hokage**"
                       f"I joined discord on {created_at}. I try my best to do every work of a **hokage**. You can get more "
                       "information on my commands by using the *dropdown* below.\n\n"
                       f"I'm also open source. You can see my code on [GitHub]({LinksAndVars.github.value})!"
                       ),
                inline=False,
            )
        elif self.index == 1:
            entries = (
                ("<argument>", "This means the argument is __**required**__."),
                ("[argument]", "This means the argument is __**optional**__."),
                ("[A|B]", "This means that it can be __**either A or B**__."),
                (
                    "[argument...]",
                    "This means you can have multiple arguments.\n"
                    "Now that you know the basics, it should be noted that...\n"
                    "__**You do not type in the brackets!**__",
                ),
            )

            embed.add_field(
                name="How do I use this bot?",
                value="Reading the bot signature is pretty simple.",
            )

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)

        return embed

class HelpMenu(RoboPages):
    def __init__(self, source: menus.PageSource, ctx: commands.Context):
        super().__init__(source, ctx=ctx, compact=True)
    
    def add_categories(
            self, commands: Dict[commands.Cog,
                                 List[commands.Command]]) -> None:
        self.clear_items()
        for i,command_sliced in enumerate(chunks(commands, DEFAULT_COMMAND_SELECT_LENGTH-1)):
            if i>0:
                self.add_item(HelpSelectMenu(command_sliced, self.ctx.bot, add_index=False))
            else:
                self.add_item(HelpSelectMenu(command_sliced, self.ctx.bot))
        self.fill_items()

    async def rebind(self, source: menus.PageSource,
                     interaction: discord.Interaction) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                "cooldown":
                commands.CooldownMapping.from_cooldown(
                    1, 3.0, commands.BucketType.member),
                "help":
                "Shows help about the bot, a command, or a category",
            })

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent:
                fmt = f"{parent} {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent else f"{parent} {command.name}"
        return f"{alias} {command.signature}"

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        def key(command) -> str:
            cog = command.cog
            return cog.qualified_name if cog else "\U0010ffff"

        entries: List[commands.Command] = await self.filter_commands(
            bot.commands, sort=True, key=key)

        all_commands: Dict[commands.Cog, List[commands.Command]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == "\U0010ffff":
                continue

            cog = bot.get_cog(name)
            all_commands[cog] = sorted(children,
                                       key=lambda c: c.qualified_name)

        menu = HelpMenu(FrontPageSource(), ctx=self.context)
        for command_sliced in chunks(all_commands, DEFAULT_COMMAND_SELECT_LENGTH):
            menu.add_categories(command_sliced)
        await menu.start()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        menu = HelpMenu(
            GroupHelpPageSource(cog, entries,
                                prefix=self.context.clean_prefix),
            ctx=self.context,
        )
        await menu.start()

    def common_command_formatting(self, embed_like, command):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f"{command.description[:100]}\n\n{command.help}"
        else:
            embed_like.description = command.help or "No help found..."

    async def send_command_help(self, command):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour(0xA8B9CD))
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group,
                                     entries,
                                     prefix=self.context.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source, ctx=self.context)
        await menu.start()
