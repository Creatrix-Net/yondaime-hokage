import discord
from discord.ext import commands
from lib import BackupDatabse, SuccessEmbed


class BackUp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.description = "Create a backup for your server"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f4be")

    @commands.command(description="Create backup of the server")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(2, 60, commands.BucketType.guild)
    async def backup(self, ctx):
        """
        Create a backup of this guild, (it backups only those channels which is visible to the bot)
        And then dm you the backup code, (Phew keep it safe)
        """
        if not await ctx.prompt(
                f"Are you sure that you want to **create a backup** of this guild?",
                author_id=ctx.author.id,
        ):
            return
        backup_code = await BackupDatabse(ctx).create_backup()
        backup_code_reference = await ctx.author.send(
            f":arrow_right:  **BACKUP CODE** : ``{backup_code}``")
        await ctx.send(
            content=f"{ctx.author.mention} check your dm(s) :white_check_mark:",
            embed=SuccessEmbed(
                title="The backup code was generated successfully",
                url=backup_code_reference.jump_url,
            ),
        )

    @commands.command(description="Gets the json file which is stored")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(2, 60, commands.BucketType.guild)
    async def get_backup_data(self, ctx, code: commands.MessageConverter):
        backup_code_data_url = await BackupDatabse(ctx).get_backup_data(code)
        if backup_code_data_url is not None:
            await ctx.send(
                content=f"The data for the :arrow_right: {code}\n{backup_code_data_url}"
            )
        else:
            await ctx.send(
                f"Hey {ctx.author.mention}, \n there is no data associated with **{code}** backup code!"
            )


def setup(bot):
    bot.add_cog(BackUp(bot))
