import io
from typing import Optional, Tuple, Union

import discord
from discord import CategoryChannel, Role, StageChannel, TextChannel, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Context
from orjson import dumps, loads

from ..util.vars import ChannelAndMessageId


class BackupDatabse:
    """The database class to handle the backup commands"""

    def __init__(self, ctx: Context):
        self.ctx: commands.Context = ctx
        self.backup_channel: TextChannel = ctx.get_config_channel_by_name_or_id(
            ChannelAndMessageId.backup_channel.value
        )

    async def create_backup(self) -> int:
        """|coro|
        It creates the backup of the server

        :return: The backup code
        :rtype: int
        """
        roles_dict = {}
        fetch_roles = await self.ctx.guild.fetch_roles()
        for i in fetch_roles:
            if not i.managed or not i.is_integration() or not i.is_premium_subscriber():
                roles_dict.update(
                    {
                        i.name: {
                            "colour": i.colour.value,
                            "hoist": i.hoist,
                            "position": i.position,
                            "mentionable": i.mentionable,
                            "permission": i.permissions.value,
                        }
                    }
                )

        text_channel = {}
        category_channel = {}
        voice_channel = {}
        stage_channel = {}
        fetch_channels = await self.ctx.guild.fetch_channels()
        for i in fetch_channels:
            if isinstance(i, CategoryChannel):
                category_channel_update_dict = {
                    "nsfw": i.nsfw,
                    "position": i.position,
                    "role_overwrites": {},
                }
                for j in i.overwrites:
                    role_overwrites = {}
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.update(
                                {
                                    j.name: {
                                        "allow": value.pair()[0].value,
                                        "deny": value.pair()[-1].value,
                                    }
                                }
                            )
                    category_channel_update_dict.update(
                        {"role_overwrites": role_overwrites}
                    )
                category_channel.update({i.name: category_channel_update_dict})

            elif isinstance(i, VoiceChannel):
                voice_channel_update_dict = {
                    "position": i.position,
                    "bitrate": i.bitrate,
                    "permissions_synced": i.permissions_synced,
                    "video_quality_mode": i.video_quality_mode.name,
                    "category": None if i.category is None else i.category.name,
                    "user_limit": i.user_limit,
                    "role_overwrites": {},
                }
                for j in i.overwrites:
                    role_overwrites = {}
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.update(
                                {
                                    key.name: {
                                        "allow": value.pair()[0].value,
                                        "deny": value.pair()[-1].value,
                                    }
                                }
                            )
                    voice_channel_update_dict.update(
                        {"role_overwrites": role_overwrites}
                    )
                voice_channel.update({i.name: voice_channel_update_dict})

            elif isinstance(i, TextChannel):
                text_channel_update_dict = {
                    "nsfw": i.nsfw,
                    "position": i.position,
                    "slowmode_delay": i.slowmode_delay,
                    "default_auto_archive_duration": i.default_auto_archive_duration,
                    "category": None if i.category is None else i.category.name,
                    "topic": i.topic,
                    "permissions_synced": i.permissions_synced,
                    "role_overwrites": {},
                }
                for j in i.overwrites:
                    role_overwrites = {}
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.update(
                                {
                                    key.name: {
                                        "allow": value.pair()[0].value,
                                        "deny": value.pair()[-1].value,
                                    }
                                }
                            )
                    text_channel_update_dict.update(
                        {"role_overwrites": role_overwrites}
                    )
                text_channel.update({i.name: text_channel_update_dict})

            elif isinstance(i, StageChannel):
                stage_channel_update_dict = {
                    "position": i.position,
                    "bitrate": i.bitrate,
                    "permissions_synced": i.permissions_synced,
                    "video_quality_mode": i.video_quality_mode.name,
                    "topic": i.topic,
                    "category": None if i.category is None else i.category.name,
                    "user_limit": i.user_limit,
                    "role_overwrites": {},
                }
                for j in i.overwrites:
                    role_overwrites = {}
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.update(
                                {
                                    key.name: {
                                        "allow": value.pair()[0].value,
                                        "deny": value.pair()[-1].value,
                                    }
                                }
                            )
                    stage_channel_update_dict.update(
                        {"role_overwrites": role_overwrites}
                    )
                stage_channel.update({i.name: stage_channel_update_dict})
        json_bytes = dumps(
            {
                "roles": roles_dict,
                "category_channel": category_channel,
                "text_channels": text_channel,
                "voice_channel": voice_channel,
                "stage_channel": stage_channel,
            }
        )
        message_reference = await self.backup_channel.send(
            content=self.ctx.guild.id,
            file=discord.File(
                io.BytesIO(json_bytes), filename=f"{self.ctx.guild.id}.json"
            ),
        )
        return message_reference.id

    async def get_backup_data(self, code: int) -> Optional[discord.Attachment]:
        """|coro|
        It returns the backup of the specified server

        :param code: The message containing that backup
        :type code: int
        :return: The json file which has the backup
        :rtype: Optional[discord.Attachment]
        """
        try:
            code = await commands.MessageConverter().convert(
                self.ctx,
                f"https://discord.com/channels/{ChannelAndMessageId.server_id2.value}/{ChannelAndMessageId.backup_channel.value}/{code}",
            )
        except (
            commands.CommandError,
            commands.BadArgument,
            commands.ChannelNotFound,
            commands.MessageNotFound,
            commands.ChannelNotReadable,
        ):
            return
        return code.attachments[0] if code else None

    async def delete_backup_data(
        self,
        code: int,
    ):
        """|coro|
        Deletes the backup data against the specified code

        :param code: The backup code to delete
        :type code: int
        """
        try:
            code = await commands.MessageConverter().convert(
                self.ctx,
                f"https://discord.com/channels/{ChannelAndMessageId.server_id2.value}/{ChannelAndMessageId.backup_channel.value}/{code}",
            )
        except (
            commands.CommandError,
            commands.BadArgument,
            commands.ChannelNotFound,
            commands.MessageNotFound,
            commands.ChannelNotReadable,
        ):
            return
        await code.delete()
        return

    async def apply_backup(self, code: int) -> Optional[Union[str, bool]]:
        """|coro|
        It applied backup with the backup code specified

        :param code:Backup Code
        :type code: int
        :return: :class:`str` is returned when there is a error otherwise a :class:`bool` with True value
        :rtype: Optional[Union[str, bool]]
        """
        backup: Optional[discord.Attachment] = await self.get_backup_data(code)
        if backup is None:
            return "No backup with that id exists"
        try:
            data = await backup.read()
        except (discord.HTTPException, discord.Forbidden, discord.NotFound) as e:
            print(e)
            return "Can't apply due to some permission error"
        data = loads(data)
        guild = self.ctx.guild

        roles = data["roles"]
        for j in roles:
            try:
                role_in_server = await commands.RoleConverter().convert(self.ctx, j)
                await role_in_server.edit(
                    reason=self.reason(code, self.ctx.author),
                    colour=roles[j]["colour"],
                    hoist=roles[j]["hoist"],
                    mentionable=roles[j]["mentionable"],
                    permissions=discord.Permissions(roles[j]["permission"]),
                )
                try:
                    if not roles[j]["position"] <= 0:
                        await role_in_server.edit(
                            position=roles[j]["position"],
                            reason=self.reason(code, self.ctx.author),
                        )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

            except (commands.RoleNotFound, commands.CommandError, commands.BadArgument):
                created_role = await guild.create_role(
                    reason=self.reason(code, self.ctx.author),
                    name=j,
                    colour=roles[j]["colour"],
                    hoist=roles[j]["hoist"],
                    mentionable=roles[j]["mentionable"],
                    permissions=discord.Permissions(roles[j]["permission"]),
                )
                try:
                    if not roles[j]["position"] <= 0:
                        await created_role.edit(
                            position=roles[j]["position"],
                            reason=self.reason(code, self.ctx.author),
                        )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

        category_data = data["category_channel"]
        for i in category_data:
            try:
                category_channel = await commands.CategoryChannelConverter().convert(
                    self.ctx, i
                )

                await category_channel.edit(
                    position=category_data[i]["position"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        category_data[i]["role_overwrites"]
                    ),
                    nsfw=category_data[i]["nsfw"],
                )
            except (
                commands.ChannelNotFound,
                commands.BadArgument,
                commands.CommandError,
            ):
                created_category = await guild.create_category(
                    reason=self.reason(code, self.ctx.author),
                    position=category_data[i]["position"],
                    overwrites=await self.return_role_overwrites(
                        category_data[i]["role_overwrites"]
                    ),
                    name=i,
                )
                try:
                    await created_category.edit(
                        nsfw=category_data[i]["nsfw"],
                        reason=self.reason(code, self.ctx.author),
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

        text_data = data["text_channels"]
        for i in text_data:
            try:
                text_channel = await commands.TextChannelConverter().convert(
                    self.ctx, i
                )
                await text_channel.edit(
                    position=text_data[i]["position"],
                    nsfw=text_data[i]["nsfw"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        text_data[i]["role_overwrites"]
                    ),
                    slowmode_delay=text_data[i]["slowmode_delay"],
                    default_auto_archive_duration=text_data[i][
                        "default_auto_archive_duration"
                    ],
                    topic=text_data[i]["topic"],
                    permissions_synced=text_data[i]["permissions_synced"],
                    category=await self.return_category_channel(
                        text_data[i]["category"]
                    ),
                )
            except (
                commands.ChannelNotFound,
                commands.BadArgument,
                commands.CommandError,
            ):
                created_text = await guild.create_text_channel(
                    reason=self.reason(code, self.ctx.author),
                    nsfw=text_data[i]["nsfw"],
                    position=text_data[i]["position"],
                    overwrites=await self.return_role_overwrites(
                        text_data[i]["role_overwrites"]
                    ),
                    slowmode_delay=text_data[i]["slowmode_delay"],
                    topic=text_data[i]["topic"],
                    category=await self.return_category_channel(
                        text_data[i]["category"]
                    ),
                    name=i,
                )
                try:
                    await created_text.edit(
                        default_auto_archive_duration=text_data[i][
                            "default_auto_archive_duration"
                        ],
                        permissions_synced=text_data[i]["permissions_synced"],
                        reason=self.reason(code, self.ctx.author),
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

        voice_data = data["voice_channel"]
        for i in voice_data:
            try:
                voice_channel = await commands.VoiceChannelConverter().convert(
                    self.ctx, i
                )
                await voice_channel.edit(
                    position=voice_data[i]["position"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        voice_data[i]["role_overwrites"]
                    ),
                    bitrate=voice_data[i]["bitrate"],
                    permissions_synced=voice_data[i]["permissions_synced"],
                    video_quality_mode=discord.VideoQualityMode[
                        voice_data[i]["video_quality_mode"]
                    ],
                    user_limit=voice_data[i]["user_limit"],
                    category=await self.return_category_channel(
                        voice_data[i]["category"]
                    ),
                )
            except (
                commands.ChannelNotFound,
                commands.BadArgument,
                commands.CommandError,
            ):
                created_voice = await guild.create_voice_channel(
                    position=voice_data[i]["position"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        voice_data[i]["role_overwrites"]
                    ),
                    bitrate=voice_data[i]["bitrate"],
                    video_quality_mode=discord.VideoQualityMode[
                        voice_data[i]["video_quality_mode"]
                    ],
                    user_limit=voice_data[i]["user_limit"],
                    category=await self.return_category_channel(
                        voice_data[i]["category"]
                    ),
                    name=i,
                )
                try:
                    await created_voice.edit(
                        permissions_synced=voice_data[i]["permissions_synced"],
                        reason=self.reason(code, self.ctx.author),
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

        stage_data = data["stage_channel"]
        for i in stage_data:
            try:
                voice_channel = await commands.StageChannelConverter().convert(
                    self.ctx, i
                )
                await voice_channel.edit(
                    position=stage_data[i]["position"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        stage_data[i]["role_overwrites"]
                    ),
                    bitrate=stage_data[i]["bitrate"],
                    permissions_synced=stage_data[i]["permissions_synced"],
                    video_quality_mode=discord.VideoQualityMode[
                        stage_data[i]["video_quality_mode"]
                    ],
                    user_limit=stage_data[i]["user_limit"],
                    topic=stage_data[i]["topic"],
                    category=await self.return_category_channel(
                        stage_data[i]["category"]
                    ),
                )
            except (
                commands.ChannelNotFound,
                commands.BadArgument,
                commands.CommandError,
            ):
                created_stage = await guild.create_stage_channel(
                    position=stage_data[i]["position"],
                    reason=self.reason(code, self.ctx.author),
                    overwrites=await self.return_role_overwrites(
                        stage_data[i]["role_overwrites"]
                    ),
                    topic=stage_data[i]["topic"],
                    category=await self.return_category_channel(
                        stage_data[i]["category"]
                    ),
                    name=i,
                )
                try:
                    await created_stage.edit(
                        permissions_synced=voice_data[i]["permissions_synced"],
                        reason=self.reason(code, self.ctx.author),
                        video_quality_mode=discord.VideoQualityMode[
                            stage_data[i]["video_quality_mode"]
                        ],
                        bitrate=stage_data[i]["bitrate"],
                        user_limit=stage_data[i]["user_limit"],
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.InvalidArgument,
                ):
                    pass

    async def return_category_channel(
        self, name: str
    ) -> Optional[discord.CategoryChannel]:
        """It returns the category channel from the category name

        :param name: Category channel name
        :type name: str
        :return: See Above
        :rtype: Optional[discord.CategoryChannel]
        """
        try:
            return await commands.CategoryChannelConverter().convert(self.ctx, name)
        except (commands.ChannelNotFound, commands.BadArgument, commands.CommandError):
            return

    async def return_role_overwrites(self, data: dict) -> dict:
        """Return the role overwrites dict with proper formatting

        :param data: Dict containing the role overwrites data
        :type data: dict
        :return: Role Overwrites with the proper formatting
        :rtype: dict
        """
        role_overwrites = {}
        for j in data:
            for k in j:
                object_role_or_member = None
                try:
                    object_role_or_member = await commands.RoleConverter().convert(
                        self.ctx, k
                    )
                except (
                    commands.RoleNotFound,
                    commands.CommandError,
                    commands.BadArgument,
                ):
                    try:
                        object_role_or_member = (
                            await commands.MemberConverter().convert(self.ctx, k)
                        )
                    except (
                        commands.MemberNotFound,
                        commands.CommandError,
                        commands.BadArgument,
                    ):
                        pass
                if object_role_or_member is not None:
                    role_overwrites.update(
                        {
                            object_role_or_member: discord.PermissionOverwrite(
                                allow=j[k]["allow"], deny=j[k]["deny"]
                            )
                        }
                    )
        return role_overwrites

    @staticmethod
    def reason(
        code: int, author: Optional[Union[discord.Member, discord.User]] = None
    ) -> str:
        """It generates the mod reason

        :param code: The backup code
        :type code: int
        :param author: The author who is using the backup, defaults to None
        :type author: Optional[Union[discord.Member, discord.User]], optional
        :return: The reason to be given in the `reason` parameter
        :rtype: str
        """
        if author is None:
            return f"Backup applied [ID: {code}]"
        return f"Backup applied [ID: {code}] by {author} [ID : {author.id}]"
