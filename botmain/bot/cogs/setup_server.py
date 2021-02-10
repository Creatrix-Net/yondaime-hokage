import discord
from discord.ext import commands
import asyncio

class Server_Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='setup',description="Easy setup for the server")
    async def _setup(self,ctx):
        admin_roles = [role for role in ctx.guild.roles if role.permissions.administrator and not role.managed]
        overwrite_dict = {}
        for i in admin_roles:
            overwrite_dict[i] = discord.PermissionOverwrite(read_messages=True)
        overwrite_dict.update({ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),ctx.guild.me: discord.PermissionOverwrite(read_messages=True)})
        await ctx.guild.create_category("Admin / Feedback", overwrites = overwrite_dict, reason="To log the admin and feedback events")
        
        #Bot Setup Channel
        botask = await ctx.guild.create_text_channel("Bot Setup", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
        
        #Feedback
        feedback = await botask.send(f"@here Want to create a feedback system for the **{ctx.guild.name}** ? \n If yes please react with :white_check_mark: and **if no** please react with **any emoji!**")
        await feedback.add_reaction('\u2705')
        try:
            _, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda _reaction, user: _reaction.message.ctx.guild == ctx.guild
                    and _reaction.message.channel == feedback
                    and _reaction.message == ctx.guild and user != ctx.guild.bot.user
                    and not user.bot,
                    timeout=60,)
        except asyncio.TimeoutError:
            await ctx.guild.create_text_channel("Feedback", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
            return await botask.edit(embed=discord.Embed(description="No reaction from the **Administrators**!! So creating all **Channels and roles as per my requirements!** for the feedback system for the **{ctx.guild.name}**"))
        if str(_.emoji) == '\u2705':
            await ctx.guild.create_text_channel("Feedback", category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
        else:
            await feedback.edit(f'**Okay** no feedback system will be there for the **{ctx.guild.name}**')

        #Support
        support = await botask.send(f"@here Want to create a support system for the **{ctx.guild.name}** ? \n If yes please react with :white_check_mark: and **if no** please react with **any emoji!**")
        await support.add_reaction('\u2705')
        try:
            _, user = await ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda _reaction, user: _reaction.message.ctx.guild == ctx.guild
                    and _reaction.message.channel == support
                    and _reaction.message == ctx.guild and user != ctx.guild.bot.user
                    and not user.bot,
                    timeout=60,)
        except asyncio.TimeoutError:
            await ctx.guild.create_role(name="Support Required")
            overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support Required"): discord.PermissionOverwrite(read_messages=False)})
            await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
            return await support.edit(embed=discord.Embed(description=f"No reaction from the **Administrators**!! So creating all **Channels and roles as per my requirements!** for the support system for the **{ctx.guild.name}**"))
        if str(_.emoji) == '\u2705':
            await ctx.guild.create_role(name="Support Required")
            overwrite_dict.update({discord.utils.get(ctx.guild.roles,name="Support Required"): discord.PermissionOverwrite(read_messages=False)})
            await ctx.guild.create_text_channel("Support", overwrites=overwrite_dict,category=discord.utils.get(ctx.guild.categories, name="Admin / Feedback"))
        else:
            await support.edit(f'**Okay** no support system will be there for the **{ctx.guild.name}**')   
        #Setup Finish
        await discord.utils.get(ctx.guild.channels,name="Bot Setup").delete()

def setup(bot):
    bot.add_cog(Server_Setup(bot))
