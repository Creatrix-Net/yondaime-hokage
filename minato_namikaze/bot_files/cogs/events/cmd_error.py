import traceback

import discord
import io
from discord.ext import commands

from ...lib import ChannelAndMessageId, Embed, ErrorEmbed


class BotEventsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_report_channel = self.bot.get_channel(
            ChannelAndMessageId.error_logs_channel.value
        )
        self.traceback_channel = self.bot.get_channel(
            ChannelAndMessageId.traceback_channel.value
        )
        self.delete_after_time = 5

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            e1 = ErrorEmbed(title="Command Error!", description=f"`{error}`")
            e1.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e1, delete_after=self.delete_after_time)

        elif isinstance(error, commands.MissingRequiredArgument):
            e4 = ErrorEmbed(title="Command Error!", description=f"`{error}`")
            e4.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e4, delete_after=self.delete_after_time)

        elif isinstance(error, commands.CommandNotFound):
            e2 = ErrorEmbed(title="Command Error!", description=f"`{error}`")
            e2.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e2, delete_after=self.delete_after_time)

        elif isinstance(error, commands.BotMissingPermissions):
            e = ErrorEmbed(description=error)
            await ctx.send(embed=e, delete_after=self.delete_after_time)

        elif isinstance(error, commands.MissingPermissions):
            e = ErrorEmbed(description=error)
            await ctx.send(embed=e, delete_after=self.delete_after_time)

        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                embed=Embed(
                    description=f"There was something **wrong** with your **input**!\n Please type\n ```)help {ctx.command.name}```,\n to know how to use the command"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.NotOwner):
            return

        elif isinstance(error, commands.CheckFailure):
            return

        elif isinstance(error, commands.CheckAnyFailure):
            return

        elif isinstance(error, commands.EmojiNotFound):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"The emoji provided {error.argument} was **not found!**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.PartialEmojiConversionFailure):
            return

        elif isinstance(error, commands.BadInviteArgument):
            return

        elif isinstance(error, commands.PartialEmojiConversionFailure):
            return

        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.NSFWChannelRequired):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"{error.channel.mention} is an **NSFW Channel**! **{ctx.command.name}** can be run only in **NSFW Channels**! :triumph:"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.MissingRole):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"You **need** the following **role**: **{' '.join(error.missing_role)}**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.MissingAnyRole):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"You **need** the following **role**: **{' '.join(error.missing_roles)}**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.BotMissingRole):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"I **need** the following **role**: **{' '.join(error.missing_role)}**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.BotMissingAnyRole):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"I **need** the following **role**: **{' '.join(error.missing_roles)}**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.BadBoolArgument):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.BadColourArgument):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.MessageNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.ChannelNotReadable):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"I need the **read message history** permission in that channel! In order to execute **{ctx.command.name}**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.DisabledCommand):
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(
                embed=ErrorEmbed(description=error), delete_after=self.delete_after_time
            )

        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"**{ctx.command.name}** works only in **DM's**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=ErrorEmbed(
                    description=f"**{ctx.command.name}** doesn't work in **DM's**"
                ),
                delete_after=self.delete_after_time,
            )

        elif isinstance(error, commands.CommandOnCooldown):
            l = self.bot.get_command(ctx.command.name)
            left = l.get_cooldown_retry_after(ctx)
            e = ErrorEmbed(title=f"Cooldown left - {round(left)}")
            await ctx.send(embed=e, delete_after=self.delete_after_time)

        elif isinstance(error, commands.CommandInvokeError):
            e7 = ErrorEmbed(
                title="Oh no, I guess I have not been given proper access! Or some internal error",
                description=f"`{error}`"[:2000],
            )
            e7.add_field(name="Command Error Caused By:",
                         value=f"{ctx.command}")
            e7.add_field(name="By", value=f"{ctx.author.name}")
            e7.set_thumbnail(url="https://i.imgur.com/1zey3je.jpg")
            e7.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e7, delete_after=self.delete_after_time)

            e = Embed(
                title=f"In **{ctx.guild.name}**",
                description=f"User affected {ctx.message.author}",
            )
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon.url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner.with_format("png").url)
            e.add_field(name="**Total Members**", value=ctx.guild.member_count)
            e.add_field(
                name="**Bots**",
                value=sum(1 for member in ctx.guild.members if member.bot),
            )
            e.add_field(
                name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True
            )
            e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            await ctx.send(
                "**Error report was successfully sent**",
                delete_after=self.delete_after_time,
            )
            message_referrence = await self.error_report_channel.send(embeds=[e7, e])
            error_traceback="```python" +str(traceback.format_exc()) + "```"
            fp = io.BytesIO(str(error_traceback).encode())
            await self.traceback_channel.send(
                content=message_referrence.jump_url,
                file=discord.File(fp, filename="traceback.txt")
            )

        else:
            haaha = ctx.author.avatar.url
            e9 = ErrorEmbed(
                title="Oh no there was some error", description=f"`{error}`"[:2000]
            )
            e9.add_field(name="**Command Error Caused By**",
                         value=f"{ctx.command}")
            e9.add_field(
                name="**By**",
                value=f"**ID** : {ctx.author.id}, **Name** : {ctx.author.name}",
            )
            e9.set_thumbnail(url=f"{haaha}")
            e9.set_footer(text=f"{ctx.author.name}")
            await ctx.channel.send(embed=e9, delete_after=self.delete_after_time)
            await c.send(embed=e9)

            e = Embed(
                title=f"In **{ctx.guild.name}**",
                description=f"User affected {ctx.message.author}",
            )
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon.url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner.with_format("png").url)
            e.add_field(name="**Total Members**", value=ctx.guild.member_count)
            e.add_field(
                name="**Bots**",
                value=sum(1 for member in ctx.guild.members if member.bot),
            )
            e.add_field(
                name="**Region**", value=str(ctx.guild.region).capitalize(), inline=True
            )
            e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            await ctx.send(
                "**Error report was successfully sent**",
                delete_after=self.delete_after_time,
            )
            message_referrence = await self.error_report_channel.send(embed=e)
            error_traceback="```python" +str(traceback.format_exc()) + "```"
            fp = io.BytesIO(str(error_traceback).encode())
            await self.traceback_channel.send(
                content=message_referrence.jump_url,
                file=discord.File(fp, filename="traceback.txt")
            )


def setup(bot):
    bot.add_cog(BotEventsCommands(bot))
