import discord
from discord.ext import commands, tasks
from lib import BackupDatabse,ChannelAndMessageId
from DiscordUtils import SuccessEmbed


class BackUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Create a backup for your server"
        self.cleanup.start()

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f4be")
    
    @tasks.loop(hours=1, reconnect=True)
    async def cleanup(self):
        '''Cleans the redunadant and useless backups'''
        async for message in (await self.bot.fetch_channel(ChannelAndMessageId.backup_channel.value)).history(limit=None):
            try:
                await commands.GuildConverter().convert(await self.bot.get_context(message), message.content.strip())
            except (commands.CommandError, commands.BadArgument):
                await message.delete()
                continue
    
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(2, 60, commands.BucketType.guild)
    async def backup(self, ctx: commands.Context, command=None):
        """Backup releated commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)
            return


    @backup.command(description="Create backup of the server")
    async def create(self, ctx):
        """
        Create a backup of this guild, (it backups only those channels which is visible to the bot)
        And then dm you the backup code, (Phew keep it safe)
        """
        if not await ctx.prompt(
                "Are you sure that you want to **create a backup** of this guild?",
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

    @backup.command()
    async def get(self, ctx: commands.Context, code: int):
        """Gets the json file which is stored as a backup"""
        backup_code_data_url = await BackupDatabse(ctx).get_backup_data(code)
        if backup_code_data_url is not None:
            await ctx.send(
                content=f"The data for the ``{code}``\n{backup_code_data_url}"
            )
            return
        await ctx.send(
            f"Hey {ctx.author.mention}, \n there is no data associated with **{code}** backup code!"
        )


def setup(bot):
    bot.add_cog(BackUp(bot))
