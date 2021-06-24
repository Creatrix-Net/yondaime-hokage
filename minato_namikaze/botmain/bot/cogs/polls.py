from discord.ext import commands

from dpymenus import Page, Poll
from ..lib import convert, ErrorEmbed, Embed


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = 'Create quick polls'

    @commands.command(aliases=['stp','strawpoll','simplepoll','2optionpoll', '2optionspoll'])
    async def strawpolls(self, ctx):
        '''Create straw polls easily'''
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        questions = [
            'What should be the **strawpoll title**?',
            'Write the **description** of the strawpoll.',
            'When the this straw **should end**? type number followed **(s|m|h|d)**',
            "Enter the option/choice 1",
            "Enter the option/choice 2",
            "In which channel do you want to host this **strawpoll**?",
        ]
        
        answers = []
        
        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}",
                          description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for('message', timeout=25, check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)
        
        title, description, time = answers[0], answers[1], convert(answers[2])
        
        # Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number")
            return
        
        
        first = Page(title=title, description=description, color=discord.Color.random())
        first.set_footer(text='Only vote once! Your vote won\'t count if you cheat!')
        first.buttons(['\U00002600', '\U0001F315'])
        first.on_next(self.finish)

        second = Page(title=title, description=f'Results are in!')

        menu = Poll(ctx).set_timeout(time).add_pages([first, second])
        await menu.open()

    @staticmethod
    async def finish(menu):
        await menu.generate_results_page()
        await menu.next()


def setup(bot):
    bot.add_cog(Polls(bot))