# -*- coding: utf-8 -*-
import asyncio

import discord
from discord.ext import commands
from dpymenus import Page, Poll

from ..lib import Embed, ErrorEmbed, convert


class QuickPoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣',
                          '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

    @commands.command(pass_context=True, aliases=['poll', 'polls'])
    async def polltime(self, ctx):
        '''Create polls easily'''

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        questions = [
            'What should be the **strawpoll title**?',
            'Write the **description** of the strawpoll.',
            "How many option(s) should be there? (Min 2 and Max 10)",
            "In which channel do you want to host this **strawpoll**?",
        ]

        answers = []
        options = []

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}",
                          description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=60, check=check)
                if i == 2:
                    try:
                        int(message.content)
                    except:
                        await ctx.send(embed=ErrorEmbed(description=f'{message.content} you provided is **not an number**, Please **rerun the command again**!'))
                        return
                    if int(message.content) < 2:
                        await ctx.send(embed=ErrorEmbed(description=f'The no. of options cannot be **less than 2**, Please **rerun the command again**!'))
                        return
                    elif int(message.content) > 10:
                        await ctx.send(embed=ErrorEmbed(description=f'The no. of options cannot be **greater than 10**, Please **rerun the command again**!'))
                        return
                    else:
                        for i in range(int(message.content)):
                            await ctx.send(f'**Option {i+1}**')
                            try:
                                options_message = await self.bot.wait_for('message', timeout=60, check=check)
                            except:
                                await ctx.send("You didn't answer the questions in Time")
                                return
                            options.append(options_message.content)

            except:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)

        question, description, poll_channel = answers[0], answers[1], answers[-1]

        if not isinstance(poll_channel, discord.TextChannel):
            await ctx.send(embed=ErrorEmbed(description='Wrong text channel provided! Try again and mention the channel next time! :wink:'))
            return

        if len(options) == 2 and options[0] == 'yes' and options[1] == 'no':
            reactions = ['✅', '❌']
        else:
            reactions = self.reactions

        description = []
        for x, option in enumerate(options):
            description += '\n\n {} {}'.format(reactions[x], option)
        embed = Embed(title=question, description=''.join(description))
        react_message = await poll_channel.send(embed=embed)
        for reaction in reactions[:len(options)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text='Poll ID: {}'.format(react_message.id))
        await react_message.edit(embed=embed)

    @commands.command(pass_context=True, usage='<poll id>', aliases=['result', 'results'])
    async def tally(self, ctx, id):
        '''Get polls results'''
        try:
            poll_message = await ctx.fetch_message(id)
        except discord.NotFound:
            await ctx.send(embed=ErrorEmbed(description=f'No polls with this {id} found!'))
        except discord.Forbidden:
            await ctx.send(embed=ErrorEmbed(description='**Read Message** permission is required to execute this command!'))

        error_message = ErrorEmbed(description=f'**{id}** is not a poll!')
        if not poll_message.embeds:
            await ctx.send(embed=error_message)
            return
        embed = poll_message.embeds[0]
        if poll_message.author == ctx.message.author:
            await ctx.send(embed=error_message)
            return
        elif embed.title.startswith('(Strawpoll)') or embed.title.startswith('Results of the poll'):
            await ctx.send(embed=error_message)
            return
        else:
            try:
                if embed.footer.text.startswith('Poll ID:'):
                    await ctx.send(embed=error_message)
                    return
            except:
                await ctx.send(embed=error_message)
                return

        unformatted_options = [x.strip('\n').strip(
            ' ') for x in embed.description.split('\n') if x.strip('\n').strip(' ') != '']
        opt_dict = {}
        for x in unformatted_options:
            if x[0] != '🔟':
                opt_dict.update({x[0]: x[4:]})
            else:
                opt_dict.update({x[0]: x[1:]})

        # add the bot's ID to the list of voters to exclude it's votes
        voters = [self.bot.user.id]
        tally = {x: 0 for x in opt_dict.keys()}
        for reaction in poll_message.reactions:
            if reaction.emoji in self.reactions:
                reactors = await reaction.users().flatten()
                for reactor in reactors:
                    if reactor.id not in voters:
                        tally[str(self.reactions.index(reaction.emoji)+1)] += 1
                        voters.append(reactor.id)

        embed_result = Embed(
            title='Results of the poll for "{}":\n'.format(embed.title),
            description='\n'.join(['{} **{}**: {}\n'.format(self.reactions[i],
                                  opt_dict[key], tally[key]) for i, key in enumerate(tally.keys())])
        )
        embed.set_footer(text='Poll ID: {}'.format(id))
        await ctx.send(embed=embed_result)

    @commands.command(pass_context=True, aliases=['stf', '2poll'], usage='<emoji_option1> <emoji_option2>')
    async def strawpolls(self, ctx, emoji_option1: discord.Emoji, emoji_option2: discord.Emoji):
        '''Create straw polls easily'''
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        questions = [
            'What should be the **strawpoll title**?',
            'Write the **description** of the strawpoll.',
            "Till when this poll will be active, (s|m) (10 mins is max)"
        ]
        answers = []
        message_tuple = []
        title, description, poll_time = answers[0], answers[1], answers[2]

        time = convert(poll_time)

        # Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong", delete_after=5)
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number", delete_after=5)
            return
        elif time > 600:
            await ctx.send("The Time should not be more than 10mins", delete_after=5)
            return

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}",
                          description=question)
            question_message = await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time", delete_after=10)
                await question_message.delete()
                await message.delete()
                for i, j in question_message:
                    await i.delete()
                    await j.delete()
                    await asyncio.sleep(0.5)
                return
            answers.append(message.content)
            message_tuple.append((question_message, message))

        for i, j in question_message:
            await i.delete()
            await j.delete()
            await asyncio.sleep(0.5)

        first = Page(title='(Strawpoll) '+title,
                     description=description, color=discord.Color.random())
        first.set_footer(
            text='Only vote once! Your vote won\'t count if you cheat!')
        first.buttons([emoji_option1, emoji_option2])
        first.on_next(self.finish)

        second = Page(title='(Strawpoll) '+title,
                      description=f'Results are in!', color=discord.Color.green())

        menu = Poll(ctx).set_timeout(int(time)).add_pages([first, second])
        await menu.open()

    @staticmethod
    async def finish(menu):
        await menu.generate_results_page()
        await menu.next()


def setup(bot):
    bot.add_cog(QuickPoll(bot))
