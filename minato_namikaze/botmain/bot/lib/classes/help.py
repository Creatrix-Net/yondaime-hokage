from pretty_help import DefaultMenu, PrettyHelp
from pretty_help.pretty_help import Paginator
from discord_components import DiscordComponents, Button, ButtonStyle
from ..functions import emoji_random_func
from typing import List, Union
from ..classes import Embed

import asyncio

import discord
from discord.ext import commands


class CustomHelpPaginator(Paginator):
    def add_cog(
        self, title: Union[str, commands.Cog], commands_list: List[commands.Command], bot=None
    ):
        cog = isinstance(title, commands.Cog)
        if not commands_list:
            return

        page_title = title.qualified_name if cog else title
        if bot:
            page_title += ' ' + emoji_random_func(bot)
        embed = self._new_page(page_title, (title.description or "") if cog else "")
        self._add_command_fields(embed, page_title, commands_list)
    
    def add_command(self, command: commands.Command, signature: str, bot=None):
        desc = f"{command.description}\n\n" if command.description else ""
        page = self._new_page(
            command.qualified_name + ' '  + emoji_random_func(bot) if bot else command.qualified_name,
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
    
    @staticmethod
    def __command_info(command: Union[commands.Command, commands.Group]):
        info = ""
        if command.description:
            info += command.description + "\n\n"
        if command.help:
            info += command.help
        if not info:
            info = "None"
        return info

class MenuHelp(DefaultMenu):
    async def send_pages(
        self,
        ctx: commands.Context,
        destination: discord.abc.Messageable,
        pages: List[discord.Embed],
    ):
        total = len(pages)
        message: discord.Message = await destination.send(
            embed=pages[0],
            components = [
                    Button(
                        label = "Support Server",
                        style=ButtonStyle.URL,
                        url="https://discord.gg/g9zQbjE73K",
                        emoji = discord.utils.get(ctx.guild.emojis, id=848961696047300649)
                    ),
                ]
        )

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
        self.paginator = CustomHelpPaginator(color=self.color)
    
    async def send_command_help(self, command: commands.Command):
        filtered = await self.filter_commands([command])
        if filtered:
            self.paginator.add_command(command, self.get_command_signature(command), self.context.bot)
            await self.send_pages()
        
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
                help_filtered,
                sort=self.sort_commands,
            ):
                mapping[cmd.cog].append(cmd)
            self.paginator.add_cog(self.no_category, mapping.pop(None), bot)
            sorted_map = sorted(
                mapping.items(),
                key=lambda cg: cg[0].qualified_name
                if isinstance(cg[0], commands.Cog)
                else str(cg[0]),
            )
            for cog, command_list in sorted_map:
                self.paginator.add_cog(cog, command_list, bot)
            self.paginator.add_index(self.show_index, self.index_title + ' ' +emoji_random_func(bot), bot)
        await self.send_pages()
    
    async def send_cog_help(self, cog: commands.Cog):
        async with self.get_destination().typing():
            filtered = await self.filter_commands(
                cog.get_commands(), sort=self.sort_commands
            )
            self.paginator.add_cog(cog, filtered, self.context.bot)
        await self.send_pages()

