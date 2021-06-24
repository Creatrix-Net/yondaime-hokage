from pretty_help import DefaultMenu
from discord_components import DiscordComponents, Button, ButtonStyle

import asyncio
from typing import List

import discord
from discord.ext import commands

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
                    )
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
