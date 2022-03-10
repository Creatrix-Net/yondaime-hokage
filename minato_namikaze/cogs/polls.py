import discord
from discord.ext import commands
from DiscordUtils import Embed, ErrorEmbed
from operator import itemgetter
from typing import List

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
        self.description = 'Create polls'

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{BAR CHART}")

    @staticmethod
    async def delete_message(message_list: List[discord.Message]) -> None:
        for i in message_list:
            try:
                await i.delete()
            except (discord.Forbidden, discord.HTTPException, discord.NotFound) as e:
                print(e)
                continue

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
        all_messages = [ctx.message]

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}", description=question)
            question_message = await ctx.send(embed=embed)
            all_messages.append(question_message)
            try:
                message = await self.bot.wait_for("message",
                                                  timeout=60,
                                                  check=check)
                if i == 2:
                    all_messages.append(message)
                    try:
                        int(message.content)
                    except:
                        await ctx.send(embed=ErrorEmbed(
                            description=f"{message.content} you provided is **not an number**, Please **rerun the command again**!"
                        ), delete_after=2)
                        await self.delete_message(all_messages)
                        return
                    if int(message.content) < 2:
                        await ctx.send(embed=ErrorEmbed(
                            description="The no. of options cannot be **less than 2**, Please **rerun the command again**!"
                        ), delete_after=2)
                        await self.delete_message(all_messages)
                        return
                    if int(message.content) > len(self.reactions):
                        await ctx.send(embed=ErrorEmbed(
                            description="The no. of options cannot be **greater than 10**, Please **rerun the command again**!"
                        ), delete_after=2)
                        await self.delete_message(all_messages)
                        return
                    for i in range(int(message.content)):
                        option_question = await ctx.send(f"**Option {i+1}**")
                        all_messages.append(option_question)
                        try:
                            options_message = await self.bot.wait_for("message", timeout=60, check=check)
                            all_messages.append(option_question)
                        except:
                            await ctx.send("You didn't answer the questions in Time", delete_after=2)
                            await self.delete_message(all_messages)
                            return
                        options.append(options_message.content)

            except:
                await ctx.send("You didn't answer the questions in Time", delete_after=2)
                await self.delete_message(all_messages)
                return
            answers.append(message.content)

        question, description, poll_channel = (
            answers[0],
            answers[1],
            await
            commands.TextChannelConverter(answers[-1]).convert(ctx=ctx, argument=answers[-1]),
        )
        if not isinstance(poll_channel, discord.TextChannel):
            await ctx.send(embed=ErrorEmbed(
                description="Wrong text channel provided! Try again and mention the channel next time! :wink:"
            ),delete_after=2)
            await self.delete_message(all_messages)
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
        await ctx.send(f'Done :ok_hand: Hosted the poll in {poll_channel.mention}', delete_after=2)
        await self.delete_message(all_messages)

    @commands.command(pass_context=True,usage="<poll id>",aliases=["result", "results"])
    async def tally(self, ctx, poll_id: commands.MessageConverter):
        """Get polls results"""
        error_message = ErrorEmbed(description=f"**{poll_id.id}** is not a poll!")
        if len(poll_id.embeds) <= 0:
            await ctx.send(embed=error_message)
            return
        embed = poll_id.embeds[0]
        if poll_id.author == ctx.message.author:
            await ctx.send(embed=error_message)
            return

        if isinstance(embed.footer.text, discord.embeds._EmptyEmbed):
            await ctx.send(embed=error_message)
            return
        if not embed.footer.text.startswith('Poll'):
            await ctx.send(embed=error_message)
            return
        
        if len(poll_id.reactions) < 2:
            await ctx.send(embed=error_message)
            return
        valid_reactions = list(filter(
                lambda x: x in list(map(lambda x: str(discord.PartialEmoji(name=x.emoji)),poll_id.reactions)), 
                list(map(lambda x: str(discord.PartialEmoji(name=x.emoji)),poll_id.reactions)
            )
        ))
        if len(list(valid_reactions)) < 2:
            await ctx.send(embed=error_message)
            return
        valid_reactions_list = list(
            map(
                lambda x: (
                    x,
                    discord.utils.find(lambda z: str(z.emoji)==str(x), poll_id.reactions).count
                ),
                valid_reactions
            )
        )
        valid_reactions_list.sort(reverse=True)
        valid_reactions_list = [('Option', 'Reacted Counts')]+valid_reactions_list
        embed = Embed(title='Poll Results')
        lengths = [
            [len(str(x)) for x in row]
            for row in valid_reactions_list
        ]

        max_lengths = [
            max(map(itemgetter(x), lengths))
            for x in range(0, len(valid_reactions_list[0]))
        ]

        format_str = ''.join(map(lambda x: '%%-%ss | ' % x, max_lengths))
        embed.description = '```markdown\n' + (format_str % valid_reactions_list[0]) + '\n' + '-' * (sum(max_lengths) + len(max_lengths) * 3 - 1)
        for x in valid_reactions_list[1:]:
            embed.description += f'\n{format_str % x}'
        embed.description += '\n```'
        embed.timestamp = poll_id.created_at
        await ctx.send(embed=embed,reference=poll_id)

    @commands.command()
    @commands.guild_only()
    async def quickpoll(self, ctx, *questions_and_choices: str):
        """
        Makes a poll quickly.

        The first argument is the question and the rest are the choices.

        Also can't use the tally command here

        **Example:** `)quickpoll question option1 option2`
        """
        if len(questions_and_choices) < 3:
            return await ctx.send("Need at least 1 question with 2 choices.")
        if len(questions_and_choices) > 21:
            return await ctx.send("You can only have up to 20 choices.")

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send("Need Read Message History and Add Reactions permissions.")

        question = questions_and_choices[0]
        choices = list(enumerate(questions_and_choices[1:]))

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.HTTPException, discord.NotFound):
            pass

        body = "\n".join(f"{key}: {c}" for key, c in choices)
        poll = await ctx.send(f"{ctx.author} asks: **{question}**\n\n{body}")
        for emoji, _ in choices:
            await poll.add_reaction(discord.PartialEmoji(name=self.reactions[int(emoji)]))


def setup(bot):
    bot.add_cog(QuickPoll(bot))
