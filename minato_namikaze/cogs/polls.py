import asyncio

import discord
from discord.ext import commands

from lib import Embed, ErrorEmbed


class QuickPoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactions = [
            "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER E}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER K}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER M}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER O}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Q}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER S}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER U}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER W}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Y}",
            "\N{REGIONAL INDICATOR SYMBOL LETTER Z}",
        ]

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{BAR CHART}")

    @commands.command(pass_context=True, aliases=["poll", "polls"])
    async def polltime(self, ctx):
        """Create polls easily"""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        questions = [
            "What should be the **strawpoll title**?",
            "Write the **description** of the strawpoll.",
            "How many option(s) should be there? (Min 2 and Max 10)",
            "In which channel do you want to host this **strawpoll**?",
        ]

        answers = []
        options = []

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}", description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for("message",
                                                  timeout=60,
                                                  check=check)
                if i == 2:
                    try:
                        int(message.content)
                    except:
                        await ctx.send(embed=ErrorEmbed(
                            description=f"{message.content} you provided is **not an number**, Please **rerun the command again**!"
                        ))
                        return
                    if int(message.content) < 2:
                        await ctx.send(embed=ErrorEmbed(
                            description="The no. of options cannot be **less than 2**, Please **rerun the command again**!"
                        ))
                        return
                    if int(message.content) > len(self.reactions):
                        await ctx.send(embed=ErrorEmbed(
                            description="The no. of options cannot be **greater than 10**, Please **rerun the command again**!"
                        ))
                        return
                    for i in range(int(message.content)):
                        await ctx.send(f"**Option {i+1}**")
                        try:
                            options_message = await self.bot.wait_for(
                                "message", timeout=60, check=check)
                        except:
                            await ctx.send(
                                "You didn't answer the questions in Time")
                            return
                        options.append(options_message.content)

            except:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)

        question, description, poll_channel = (
            answers[0],
            answers[1],
            await
            commands.TextChannelConverter(answers[-1]
                                          ).convert(ctx=ctx,
                                                    argument=answers[-1]),
        )
        if not isinstance(poll_channel, discord.TextChannel):
            await ctx.send(embed=ErrorEmbed(
                description="Wrong text channel provided! Try again and mention the channel next time! :wink:"
            ))
            return

        if len(options) == 2 and options[0] == "yes" and options[1] == "no":
            reactions = ["\U00002705", "\U0000274c"]
        else:
            reactions = self.reactions

        description = []
        for x, option in enumerate(options):
            description += "\n\n {} {}".format(reactions[x], option)
        embed = Embed(title=question, description="".join(description))
        react_message = await poll_channel.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text="Poll ID: {}".format(react_message.id))
        await react_message.edit(embed=embed)

    @commands.command(pass_context=True,
                      usage="<poll id>",
                      aliases=["result", "results"])
    async def tally(self, ctx, id):
        """Get polls results"""
        try:
            poll_message = await ctx.fetch_message(id)
        except discord.NotFound:
            await ctx.send(embed=ErrorEmbed(
                description=f"No polls with this {id} found!"))
        except discord.Forbidden:
            await ctx.send(embed=ErrorEmbed(
                description="**Read Message** permission is required to execute this command!"
            ))

        error_message = ErrorEmbed(description=f"**{id}** is not a poll!")
        if not poll_message.embeds:
            await ctx.send(embed=error_message)
            return
        embed = poll_message.embeds[0]
        if poll_message.author == ctx.message.author:
            await ctx.send(embed=error_message)
            return
        if embed.title.startswith("(Strawpoll)") or embed.title.startswith(
                "Results of the poll"):
            await ctx.send(embed=error_message)
            return
        try:
            if embed.footer.text.startswith("Poll ID:"):
                await ctx.send(embed=error_message)
                return
        except:
            await ctx.send(embed=error_message)
            return

        unformatted_options = [
            x.strip("\n").strip(" ") for x in embed.description.split("\n")
            if x.strip("\n").strip(" ") != ""
        ]
        opt_dict = {}
        for x in unformatted_options:
            opt_dict.update({x[0]: x[1:]})

        # add the bot's ID to the list of voters to exclude it's votes
        voters = [self.bot.user.id]
        tally = {x: 0 for x in opt_dict}
        for reaction in poll_message.reactions:
            if reaction.emoji in self.reactions:
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if reactor.id not in voters:
                        tally[str(self.reactions.index(reaction.emoji) +
                                  1)] += 1
                        voters.append(reactor.id)

        embed_result = Embed(
            title='Results of the poll for "{}":\n'.format(embed.title),
            description="\n".join([
                "{} **{}**: {}\n".format(self.reactions[i], opt_dict[key],
                                         tally[key])
                for i, key in enumerate(tally.keys())
            ]),
        )
        embed.set_footer(text="Poll ID: {}".format(id))
        await ctx.send(embed=embed_result)

    @commands.command()
    @commands.guild_only()
    async def strawpoll(self, ctx, *, question):
        """Interactively creates a poll with the following question.

        To vote, use reactions!

        Also can't use the tally command here
        """
        # a list of messages to delete when we're all done
        messages = [ctx.message]
        answers = []

        def check(m):
            return (m.author == ctx.author and m.channel == ctx.channel
                    and len(m.content) <= 100)

        for i in range(20):
            messages.append(await ctx.send(
                f"Say poll option or {ctx.prefix}cancel to publish poll."))

            try:
                entry = await self.bot.wait_for("message",
                                                check=check,
                                                timeout=60.0)
            except asyncio.TimeoutError:
                break

            messages.append(entry)

            if entry.clean_content.startswith(f"{ctx.prefix}cancel"):
                break

            answers.append(i, entry.clean_content)

        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass  # oh well

        answer = "\n".join(f"{keycap}: {content}"
                           for keycap, content in answers)
        actual_poll = await ctx.send(
            f"{ctx.author} asks: {question}\n\n{answer}")
        for emoji, _ in answers:
            await actual_poll.add_reaction(emoji)

    @strawpoll.error
    async def poll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(
                embed=ErrorEmbed(description="Missing the question."),
                delete_after=5)

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """
        Makes a poll quickly.

        The first argument is the question and the rest are the choices.

        Also can't use the tally command here
        """
        if len(questions_and_choices) < 3:
            return await ctx.send("Need at least 1 question with 2 choices.")
        if len(questions_and_choices) > 21:
            return await ctx.send("You can only have up to 20 choices.")

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send(
                "Need Read Message History and Add Reactions permissions.")

        question = questions_and_choices[0]
        choices = list(enumerate(questions_and_choices[1:]))

        try:
            await ctx.message.delete()
        except:
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f"{ctx.author} asks: {question}\n\n{body}")
        for emoji, _ in choices:
            await poll.add_reaction(emoji)


def setup(bot):
    bot.add_cog(QuickPoll(bot))
