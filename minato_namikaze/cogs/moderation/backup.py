import discord
from discord.ext import commands, tasks
from lib import BackupDatabse,ChannelAndMessageId, Arguments
from DiscordUtils import SuccessEmbed
import shlex, argparse


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
    @commands.has_permissions(manage_guild=True, manage_channels=True, manage_roles=True)
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
    
    @backup.command()
    async def delete(self, ctx: commands.Context, *,args):
        """Deletes the backup data if it is there in the database.
        This command has a powerful "command line" syntax. To use this command
        you and the bot must both have Manage Server permission. **-all option is optional.**
        The following options are valid.
        `--id` or `-id`: Array of backup id to delete.
        `--all` or `-all`: To delete all backup(s) of the guild.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument("--id", "-id", action="append_const",const=int)
        parser.add_argument("--all", "-all", action="store_true")
        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            return await ctx.send(str(e))
        if args.id:
            if len(args.id) <= 0:
                await ctx.send('No Backup Id\'s provided')
                return
            await ctx.send("If any backup(s) with those id exists then it will deleted.")
            for i in args.id:
                await BackupDatabse(ctx).delete_backup_data(int(i))
            return
        if args.all:
            await ctx.send("If any backup(s) of the guild exists then it will be deleted.")
            async for message in (await self.bot.fetch_channel(ChannelAndMessageId.backup_channel.value)).history(limit=None):
                if int(message.content.strip()) == ctx.guild.id:
                    await message.delete()
            return
            
        await ctx.send('No arguments were provided')


def setup(bot):
    bot.add_cog(BackUp(bot))
