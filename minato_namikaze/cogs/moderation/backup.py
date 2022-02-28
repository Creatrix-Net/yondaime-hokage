import discord
from discord.ext import commands, tasks
from lib import BackupDatabse,ChannelAndMessageId, Arguments
from DiscordUtils import SuccessEmbed
import shlex, datetime, io
from typing import Optional, Union
from orjson import dumps
import time


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

    @backup.command(aliases=["channelbackup"], usage="[channel.mention | channel.id]")
    async def channellogs(
        self, 
        ctx,
        channel: Optional[Union[commands.TextChannelConverter, discord.TextChannel]] = None,
        send: Optional[Union[commands.TextChannelConverter, discord.TextChannel]] = None,
    ):
        """
        Creat a backup of all channel data as json files This might take a long time
        `channel` is partial name or ID of the server you want to backup
        defaults to the server the command was run in
        """
        if not await ctx.prompt(
                "Are you sure that you want to **message a backup** of specified channel(s)?",
                author_id=ctx.author.id,
        ):
            return
        start = time.time()
        first_message = await ctx.send(':clock1: Scanning')
        if channel is None:
            channel = ctx.channel
        if send is None:
            send = ctx.channel
        guild = ctx.guild
        today = datetime.date.today().strftime("%Y-%m-%d")
        total_msgs = 0
        message_dict = {}
        try:
            async for message in channel.history(limit=None):
                data = {
                    "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "tts": message.tts,
                    "author": {
                        "name": message.author.name,
                        "display_name": message.author.display_name,
                        "discriminator": message.author.discriminator,
                        "id": message.author.id,
                        "bot": message.author.bot,
                    },
                    "content": message.content,
                    "channel": {"name": message.channel.name, "id": message.channel.id},
                    "mention_everyone": message.mention_everyone,
                    "mentions": [
                        {
                            "name": user.name,
                            "display_name": user.display_name,
                            "discriminator": user.discriminator,
                            "id": user.id,
                            "bot": user.bot,
                        }
                        for user in message.mentions
                    ],
                    "channel_mentions": [
                        {"name": channel.name, "id": channel.id}
                        for channel in message.channel_mentions
                    ],
                    "role_mentions": [
                        {"name": role.name, "id": role.id} for role in message.role_mentions
                    ],
                    "id": message.id,
                    "pinned": message.pinned,
                }
                
                if message.attachments:
                    attachements_data = [a.url for a in message.attachments]
                    data.update({'attachements': attachements_data})
                message_dict.update({str(message.id): data})
            total_msgs += len(message_dict)
            await send.send(
                file=discord.File(io.BytesIO(dumps(message_dict)),filename=f"{guild.id}-{today}.json"),
            )
        except discord.Forbidden:
            return
        await first_message.edit("{} messages saved from `{}` \nTime taken is {} sec".format(total_msgs, channel.name, round(time.time() - start)))

    @backup.command(aliases=["serverbackup"])
    async def serverlogs(self, ctx):
        """
        Creat a backup of all server data as json files This might take a long time
        """
        if not await ctx.prompt(
                "Are you sure that you want to **create a message backup** of this guild?",
                author_id=ctx.author.id,
        ):
            return
        start = time.time()
        first_message = await ctx.send(':clock1: Scanning')
        guild = ctx.guild
        today = datetime.date.today().strftime("%Y-%m-%d")
        channel = ctx.message.channel
        total_msgs = 0
        whole_data_dict = {}
        for chn in guild.channels:
            # await channel.send("backing up {}".format(chn.name))
            message_list = []
            try:
                start_channel = time.time()
                async for message in chn.history(limit=None):
                    data = {
                        "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "tts": message.tts,
                        "author": {
                            "name": message.author.name,
                            "display_name": message.author.display_name,
                            "discriminator": message.author.discriminator,
                            "id": message.author.id,
                            "bot": message.author.bot,
                        },
                        "content": message.content,
                        "channel": {"name": message.channel.name, "id": message.channel.id},
                        "mention_everyone": message.mention_everyone,
                        "mentions": [
                            {
                                "name": user.name,
                                "display_name": user.display_name,
                                "discriminator": user.discriminator,
                                "id": user.id,
                                "bot": user.bot,
                            }
                            for user in message.mentions
                        ],
                        "channel_mentions": [
                            {"name": channel.name, "id": channel.id}
                            for channel in message.channel_mentions
                        ],
                        "role_mentions": [
                            {"name": role.name, "id": role.id} for role in message.role_mentions
                        ],
                        "id": message.id,
                        "pinned": message.pinned,
                    }
                    if message.attachments:
                        attachements_data = [a.url for a in message.attachments]
                        data.update({'attachements': attachements_data})
                    message_list.append(data)
                total_msgs += len(message_list)
                if len(message_list) == 0:
                    continue
                await channel.send("{} messages saved from `{}` \nTime taken is {} sec".format(len(message_list), chn.name, round(time.time() - start_channel)))
            except discord.errors.Forbidden:
                await channel.send("0 messages saved from `{}`".format(chn.name))
                pass
            except AttributeError:
                await channel.send("0 messages saved from `{}`".format(chn.name))
                pass
            whole_data_dict.update({str(chn.id):message_list })
        await channel.send(
            file=discord.File(io.BytesIO(dumps(whole_data_dict)),filename=f"{guild.id}-{today}.json"),
        )
        await first_message.edit("{} messages saved from `{}` \nTime taken is {} sec".format(total_msgs, guild.name, round(time.time()-start)))


    @backup.command(description="Creates a template backup of the server", aliases=['templates'])
    async def template(self, ctx):
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

    @backup.command(usage='<code>')
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
    
    @backup.command(usage='<args>')
    async def delete(self, ctx: commands.Context, *,args):
        """Deletes the backup data if it is there in the database.
        This command has a powerful "command line" syntax. To use this command
        you and the bot must both have Manage Server permission. **-all option is optional.**
        The following options are valid.
        `--id` or `-id`: Array of backup id to delete.
        `--all` or `-all`: To delete all backup(s) of the guild.
        """
        if not await ctx.prompt(
                "Are you sure that you want to **delete the backup** of this guild?",
                author_id=ctx.author.id,
        ):
            return
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
    
    @backup.command(usage='<code>')
    async def apply(self, ctx: commands.Context, code: int):
        '''Applies backup template to the server. This may take a lot of time.
        
        ```
        Note: Some things like role position, some role colours, and some channel positioning may not be applied 
        due to Discord limitations, so you may have to fine tune on your own.
        ```
        '''
        if not await ctx.prompt(
                "Are you sure that you want to **apply the template backup** to this guild?",
                author_id=ctx.author.id,
        ):
            return
        first = await ctx.send('Backup will be applied, if backup with that id exists! and this message will be deleted!')
        start = time.time()
        backup_return_value = await BackupDatabse(ctx).apply_backup(int(code))
        end=time.time()
        if isinstance(backup_return_value, str):
            await ctx.send(backup_return_value, delete_after=5)
        else:
            await ctx.send(f'Backup applied in {round(end-start)}')
        await first.delete()

def setup(bot):
    bot.add_cog(BackUp(bot))
