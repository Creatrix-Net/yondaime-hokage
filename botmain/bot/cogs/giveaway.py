import discord
from discord.ext.commands import Cog, MissingPermissions
from discord.ext.commands import command, has_permissions, has_role
from discord import Member
from discord import Embed,File
from typing import Optional
from random import choice
from asyncio import TimeoutError, sleep
from ..lib.util.util import convert

class Giveaway(Cog):
    def __init__(self,bot):
        self.bot = bot
        self.cancelled = False

    @command(name="giveaway", aliases=["gcreate", "gcr", "giftcr"])
    @has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx):
        #Ask Questions
        embed = Embed(title="Giveaway Time!!✨",
                      description="Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway",
                      color=ctx.author.color)
        await ctx.send(embed=embed)
        questions=["In Which channel do you want to host the giveaway?",
                   "For How long should the Giveaway be hosted ? type number followed (s|m|h|d)",
                   "What is the Prize?",
                   "What role should a person must have in order to enter? If no roles required then type `none`",
                   "Tasks that the person should do in order to participate? If no tasks then type `none`"]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
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

        #Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send(f"The Channel provided was wrong. The channel should be {ctx.channel.mention}")
            return

        channel = self.bot.get_channel(channel_id)

        #Check if the role is valid
        role = answers[3]
        if role.lower() in ('none', 'no', 'no roles'):
            role=None
        else:
            try:
                role_id = int(answers[3][3:-1])
            except:
                i=ctx.guild.roles
                for j in i:
                    if j.name == '@everyone':
                        i.remove(j)
                bot_roles=choice(i)
                await ctx.send(f"The role provided was wrong. The role should be like {bot_roles.mention}")
                return

        time = convert(answers[1])

        #Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        elif time == -2:
            await ctx.send("The Time was not conventional number")
            return
        prize = answers[2]

        task = answers[4]
        if task.lower() in ('none', 'no', 'no task'):
            task=None

        await ctx.send(f"Your giveaway will be hosted in {channel.mention} and will last for {answers[1]}")
        embed = Embed(title="**🎉🎉 Giveaway Time !! 🎉🎉**",
                    description=f"🎁 Win a **{prize}** today",
                    colour=0x00FFFF)
        embed.add_field(name="Hosted By:", value=ctx.author.mention)
        embed.set_image(url='https://i.imgur.com/efLKnlh.png')
        embed.add_field(name='Giveway ends in', value=f'{answers[1]} from now')
        if role:
            embed.add_field(name='Role Required', value=f'{role}')
        if task:
            embed.add_field(name=':checkered_flag: Tasks', value={task})
        newMsg = await channel.send(embed=embed)
        embed.set_footer(text=f"Giveaway ID: {newMsg.id}")
        await newMsg.edit(embed=embed)
        await newMsg.add_reaction("🎉")
        await ctx.send(f'https://discordapp.com/channels/{ctx.guild.id}/{channel_id}/{newMsg.id}')

        #Check if Giveaway Cancelled
        self.cancelled = False
        await sleep(time)
        if not self.cancelled:
            myMsg = await channel.fetch_message(newMsg.id)

            users = await myMsg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))
            
            #Check if User list is not empty
            if len(users) <= 0:
                emptyEmbed = Embed(title="**🎉🎉 Giveaway Time !! 🎉🎉**",
                                   description=f"🎁 Win a **{prize}** today")
                emptyEmbed.add_field(name="Hosted By:", value=ctx.author.mention)
                emptyEmbed.set_image(url='https://i.imgur.com/efLKnlh.png')
                emptyEmbed.set_footer(text="**No one won the Giveaway**")
                await myMsg.edit(embed=emptyEmbed)
                return
            if len(users) > 0:
                winner = choice(users)
                winnerEmbed = Embed(title="🎉🎉 Giveaway Time !! 🎉🎉",
                                    description=f"🎁 Win a **{prize}** today",
                                    colour=0x00FFFF)
                winnerEmbed.add_field(name=f"Congratulations On Winning **{prize}**", value=winner.mention)
                winnerEmbed.set_image(url="https://firebasestorage.googleapis.com/v0/b/sociality-a732c.appspot.com/o/Loli.png?alt=media&token=ab5c8924-9a14-40a9-97b8-dba68b69195d")
                await myMsg.edit(embed=winnerEmbed)
                return

    @create_giveaway.error
    async def create_giveaway_error(self, ctx, exc):
        if isinstance(exc, MissingPermissions):
            await ctx.send("You are not allowed to create Giveaways")
        

    @command(name="giftrrl", aliases=["gifreroll", "gftroll", "grr"])
    @has_permissions(manage_guild=True)
    async def giveaway_reroll(self, ctx, GiveawayID: int, channel=None):
        if not channel:
            channel = ctx.message.channel
        try:
            msg = await channel.fetch_message(GiveawayID)
        except:
            await ctx.send("The channel or ID mentioned was incorrect")
        users = await msg.reactions[0].users().flatten()
        if len(users) <= 0:
            emptyEmbed = Embed(title="🎉🎉 Giveaway Time !! 🎉🎉",
                                   description=f"🎁 Win a Prize today")
            emptyEmbed.add_field(name="Hosted By:", value=ctx.author.mention)
            emptyEmbed.set_image(url='https://i.imgur.com/efLKnlh.png')
            emptyEmbed.set_footer(text="**No one won the Giveaway**")
            await msg.edit(embed=emptyEmbed)
            return
        if len(users) > 0:
            winner = choice(users)
            winnerEmbed = Embed(title="🎉🎉 Giveaway Time !! 🎉🎉",
                                description=f"🎁 Win a Prize today",
                                colour=0x00FFFF)
            winnerEmbed.add_field(name=f"🎉 Congratulations On Winning Giveaway 🎉", value=winner.mention)
            winnerEmbed.set_image(url="https://firebasestorage.googleapis.com/v0/b/sociality-a732c.appspot.com/o/Loli.png?alt=media&token=ab5c8924-9a14-40a9-97b8-dba68b69195d")
            await msg.edit(embed=winnerEmbed)
            await channel.send(f"🎉 Congratulations **{winner.mention}** on winning the Giveaway 🎉")
            await channel.send(f'https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/{GiveawayID}')
            return

    @command(name="giftdel", aliases=["gifdel", "gftdel", "gdl"])
    @has_permissions(manage_guild=True)
    # @has_role("admin")
    async def giveaway_stop(self, ctx,GiveawayID: int, channel=None):
        if not channel: 
            channel = ctx.message.channel
        try:
            msg = await channel.fetch_message(GiveawayID)
            newEmbed = Embed(title="Giveaway Cancelled", description="The giveaway has been cancelled!!")
            #Set Giveaway cancelled
            self.cancelled = True
            await msg.edit(embed=newEmbed) 
            await ctx.send('The giveaway cancelled')
            await ctx.send(f'https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/{GiveawayID}')
        except:
            embed = Embed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.command_ready.ready_up("giveaway")

def setup(bot):
    bot.add_cog(Giveaway(bot))