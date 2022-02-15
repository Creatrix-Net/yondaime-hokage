import time
from asyncio import TimeoutError
from random import choice
from datetime import timedelta
from typing import Optional, Union

import discord
from discord.ext import commands
from discord.ext.commands import Cog, command, has_permissions
from lib import Embed, convert, LinksAndVars, ErrorEmbed, format_relative, GiveawayConfig, cache

class Giveaway(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Helps you to organise a simple giveaway."
        self.giveaway_image = "https://i.imgur.com/efLKnlh.png"
    
    @cache()
    async def get_giveaway_config(
        self,
        giveaway_id: discord.Message,
    ):
        return await GiveawayConfig.from_record(giveaway_id, self.bot)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{PARTY POPPER}")

    @command(
        name="giveaway",
        aliases=["gcreate", "gcr", "giftcr"],
    )
    @commands.guild_only()
    @has_permissions(manage_guild=True)
    async def create_giveaway(self, ctx):
        """Allowes you to to create giveaway by answering some simple questions!"""
        # Ask Questions
        embed = Embed(
            title="Giveaway Time!! \U00002728",
            description="Time for a new Giveaway. Answer the following questions in 25 seconds each for the Giveaway",
            color=ctx.author.color,
        )
        await ctx.send(embed=embed)
        questions = [
            "In Which channel do you want to host the giveaway?",
            "For How long should the Giveaway be hosted ? type number followed (s|m|h|d)",
            "What is the Prize?",
            "What role should a person must have in order to enter? If no roles required then type `none`",
            "Tasks that the person should do in order to participate? If no tasks then type `none`",
        ]
        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for i, question in enumerate(questions):
            embed = Embed(title=f"Question {i+1}", description=question)
            await ctx.send(embed=embed)
            try:
                message = await self.bot.wait_for("message",
                                                  timeout=25,
                                                  check=check)
            except TimeoutError:
                await ctx.send("You didn't answer the questions in Time")
                return
            answers.append(message.content)

        # Check if Channel Id is valid
        try:
            channel_id = int(answers[0][2:-1])
        except:
            await ctx.send(
                f"The Channel provided was wrong. The channel provided should be like {ctx.channel.mention}"
            )
            return

        channel = self.bot.get_channel(channel_id)

        # Check if the role is valid
        role = answers[3]
        if role.lower() in ("none", "no", "no roles"):
            role = None
        else:
            try:
                int(answers[3][3:-1])
            except:
                i = ctx.guild.roles
                for j in i:
                    if j.name in ("@everyone", "@here"):
                        i.remove(j)
                bot_roles = choice(i)
                await ctx.send(
                    f"The role provided was wrong. The role should be like {bot_roles.mention}"
                )
                return

        time_ends = convert(answers[1])*1000

        # Check if Time is valid
        if time == -1:
            await ctx.send("The Time format was wrong")
            return
        if time == -2:
            await ctx.send("The Time was not conventional number")
            return
        prize = answers[2]

        task = answers[4]
        if task.lower() in ("none", "no", "no task"):
            task = None

        await ctx.send(
            f"Your giveaway will be hosted in {channel.mention} and will last for {answers[1]}"
        )
        embed = Embed(
            title="**:tada::tada: Giveaway Time !! :tada::tada:**",
            description=f":gift: Win a **{prize}** today",
            colour=0x00FFFF,
        )
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_image(url=self.giveaway_image)
        embed.add_field(
            name="Giveway ends in",
            value=f"{format_relative(discord.utils.utcnow() + timedelta(milliseconds=time_ends))} from now | [Timer]{LinksAndVars.website.value}/giveaway_timer.html?start={int(time.time() * 1000)}&length={time_ends})",
        )
        if role:
            embed.add_field(name="Role Required", value=f"{role}")
        if task:
            embed.add_field(name="\U0001f3c1 Tasks", value=task)
        newMsg = await channel.send(embed=embed)
        embed.set_footer(text=f"Giveaway ID: {newMsg.id}")
        await newMsg.edit(embed=embed)
        await newMsg.add_reaction(discord.PartialEmoji(name="\U0001f389"))
        await ctx.send(
            newMsg.jump_url
        )

    @command(
        name="giftrrl",
        usage="<giveaway id> [channel]",
        aliases=["gifreroll", "gftroll", "grr","giftroll","giveawayroll", "giveaway_roll"],
    )
    @has_permissions(manage_guild=True)
    @commands.guild_only()
    async def giveaway_reroll(self, ctx, giveaway_id: Union[commands.MessageConverter, discord.Message], channel: Optional[Union[commands.TextChannelConverter, discord.TextChannel, commands.ThreadConverter]] = None):
        """
        It picks out the giveaway winners
        `Note: It dosen't checks for task, It only checks for roles if specified`
        """
        reactions = await discord.utils.get(giveaway_id.reactions, emoji=discord.PartialEmoji(name="\U0001f389"))
        if reactions is None:
            await ctx.send("The channel or ID mentioned was incorrect")
            return
        if not channel:
            channel = ctx.message.channel
        try:
            giveaway_config = await self.get_giveaway_config(giveaway_id)
        except AttributeError as e:
            await ctx.send(e)
            return
        
        reacted_users = await reactions.users().flatten()
        if discord.utils.get(reacted_users, id=ctx.me.id):
            reacted_users.remove(discord.utils.get(reacted_users, id=ctx.me.id))
        if giveaway_config.role_required is not None and len(reacted_users) <= 0:
            reacted_users = list(filter(lambda a: giveaway_config.role_required in a.roles, reacted_users))
        if len(reacted_users) <= 0:
            emptyEmbed = Embed(title="\U0001f389\U0001f389 Giveaway Time !! \U0001f389\U0001f389", description="\U0001f381 Win a Prize today")
            emptyEmbed.set_author(name=giveaway_config.host.display_name, icon_url=giveaway_config.host.display_avatar.url)
            emptyEmbed.add_field(
                name="No winners",
                value="Not enough participants to determine the winners",
            )
            emptyEmbed.set_image(url=self.giveaway_image)
            emptyEmbed.set_footer(text="No one won the Giveaway")
            await giveaway_id.edit(embed=emptyEmbed)
            await ctx.send(
                f"No one won the giveaway! As there were not enough participants!\n{giveaway_config.jump_url}"
            )
            return
        winner = choice(reacted_users)
        winnerEmbed = giveaway_config.embed
        if discord.utils.find(lambda a: a["name"].lower() == "\U0001f389 Congratulations On Winning Giveaway \U0001f389".lower(), self.embed_dict["fields"]) is not None:
            winnerEmbed.add_field(name="\U0001f389 Congratulations On Winning Giveaway \U0001f389",value=winner.mention)
        await giveaway_id.edit(embed=winnerEmbed)
        await channel.send(
            f"\U0001f389 Congratulations **{winner.mention}** on winning the Giveaway \U0001f389"
        )
        await ctx.send(
            giveaway_id.jump_url
        )
        self.get_giveaway_config.invalidate(self, giveaway_id)

    @command(
        name="giftdel",
        usage="<giveaway id> <channel>",
        aliases=["gifdel", "gftdel", "gdl"],
    )
    @has_permissions(manage_guild=True)
    @commands.guild_only()
    async def giveaway_stop(self, ctx, GiveawayID: int, channel=None):
        """Cancels the specified giveaway"""
        if not channel:
            channel = ctx.message.channel
        try:
            msg = await channel.fetch_message(GiveawayID)
            newEmbed = Embed(
                title="Giveaway Cancelled",
                description="The giveaway has been cancelled!!",
            )
            # Set Giveaway cancelled
            self.cancelled = True
            await msg.edit(embed=newEmbed)
            await ctx.send(f"The giveaway cancelled\n{msg.jump_url}")
        except:
            embed = ErrorEmbed(title="Failure!", description="Cannot cancel Giveaway")
            await ctx.send(emebed=embed)


def setup(bot):
    bot.add_cog(Giveaway(bot))
