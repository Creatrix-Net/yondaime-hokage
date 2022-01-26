import typing
from os.path import join

import discord
from discord.ext import commands

from ...lib import Embed, has_guild_permissions


class ServerSetup(commands.Cog, name="Server Setup"):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Do some necessary setup through an interactive mode."

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{HAMMER AND WRENCH}")

    @commands.group(usage="<add_type> <textchannel>")
    @commands.guild_only()
    @has_guild_permissions(manage_guild=True)
    async def add(
        self,
        ctx,
        add_type: typing.Literal["ban", "feedback", "warns", "unban"],
        channel: commands.TextChannelConverter,
    ):
        """
        This command adds logging of the following things in the specified text channel
            - ban
            - warns
            - unban
            - feedback
            - support

        Example usage:
            ``)add ban #bans``
        """

        if not await ctx.prompt(
                f"Do you really want to **log {add_type}** for **{ctx.guild.name}** in {channel.mention}?"
        ):
            return
        dict_to_add = {str(add_type): channel.id}
        guild_dict = await (await ctx.database).get(ctx.guild.id)
        if guild_dict is None:
            await (await ctx.database).set(ctx.guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await (await ctx.database).set(ctx.guild.id, guild_dict)
        print("hi")
        await ctx.send(":ok_hand:")

    @commands.command()
    @commands.guild_only()
    @has_guild_permissions(manage_guild=True)
    async def raw_data(self, ctx):
        """
        It returns the raw data which is stored in the database in the form of json
        """
        embed = Embed(title=f"Data associated with {ctx.guild.name}")
        data = await (await ctx.database).get(ctx.guild.id)
        if data is None:
            embed.description = "```\nNo data associated with this guild\n```"
            await ctx.send(embed=embed)
            return
        embed.description = "```json\n{}\n```".format(data)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ServerSetup(bot))
