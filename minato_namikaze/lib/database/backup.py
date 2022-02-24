import io
from typing import Optional

import discord
from discord import CategoryChannel, Role, StageChannel, TextChannel, VoiceChannel
from discord.ext import commands
from discord.ext.commands import Context
from orjson import dumps, loads

from ..util.vars import ChannelAndMessageId


class BackupDatabse:
    """The database class to handle the backup commands
    """
    def __init__(self, ctx: Context):
        self.ctx: commands.Context = ctx
        self.backup_channel: TextChannel = ctx.get_config_channel_by_name_or_id(ChannelAndMessageId.backup_channel.value)

    async def create_backup(self) -> int:
        """|coro|
        It creates the backup of the server

        :return: The backup code
        :rtype: int
        """        
        roles_dict = {}
        fetch_roles = await self.ctx.guild.fetch_roles()
        for i in fetch_roles:
            if not i.managed or not i.is_integration(
            ) or not i.is_premium_subscriber():
                roles_dict.update({
                    i.name: {
                        "colour": i.colour.value,
                        "hoist": i.hoist,
                        "position": i.position,
                        "mentionable": i.mentionable,
                        "permission": i.permissions.value,
                    }
                })

        text_channel = []
        category_channel = []
        voice_channel = []
        stage_channel = []
        fetch_channels = await self.ctx.guild.fetch_channels()
        for i in fetch_channels:
            if isinstance(i, CategoryChannel):
                category_channel_update_dict = {
                    "nsfw": i.nsfw,
                    "position": i.position
                }
                for j in i.overwrites.keys():
                    role_overwrites = []
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.append({
                                j.name: {
                                    "allow": value.pair()[0].value,
                                    "deny": value.pair()[-1].value,
                                }
                            })
                    category_channel_update_dict.update(
                        {"role_overwrites": role_overwrites})
                category_channel.append({i.name: category_channel_update_dict})

            elif isinstance(i, VoiceChannel):
                voice_channel_update_dict = {"position": i.position}
                for j in i.overwrites.keys():
                    role_overwrites = []
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.append({
                                key.name: {
                                    "allow": value.pair()[0].value,
                                    "deny": value.pair()[-1].value,
                                }
                            })
                    voice_channel_update_dict.update(
                        {"role_overwrites": role_overwrites})
                voice_channel.append({i.name: voice_channel_update_dict})

            elif isinstance(i, TextChannel):
                text_channel_update_dict = {
                    "nsfw": i.nsfw,
                    "position": i.position
                }
                for j in i.overwrites.keys():
                    role_overwrites = []
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.append({
                                key.name: {
                                    "allow": value.pair()[0].value,
                                    "deny": value.pair()[-1].value,
                                }
                            })
                    text_channel_update_dict.update(
                        {"role_overwrites": role_overwrites})
                text_channel.append({i.name: text_channel_update_dict})

            elif isinstance(i, StageChannel):
                stage_channel_update_dict = {
                    "nsfw": i.nsfw,
                    "position": i.position
                }
                for j in i.overwrites.keys():
                    role_overwrites = []
                    if isinstance(j, Role):
                        for key, value in i.overwrites.items():
                            role_overwrites.apppend({
                                key.name: {
                                    "allow": value.pair()[0].value,
                                    "deny": value.pair()[-1].value,
                                }
                            })
                    stage_channel_update_dict.update(
                        {"role_overwrites": role_overwrites})
                stage_channel.append({i.name: stage_channel_update_dict})
        json_bytes = dumps({
            "roles": roles_dict,
            "category_channel": category_channel,
            "text_channels": text_channel,
            "voice_channel": voice_channel,
            "stage_channel": stage_channel,
        })
        message_reference = await self.backup_channel.send(
            content=self.ctx.guild.id,
            file=discord.File(io.BytesIO(json_bytes),
                              filename=f"{self.ctx.guild.id}.json"),
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
            code = await commands.MessageConverter().convert(self.ctx, f'https://discord.com/channels/{ChannelAndMessageId.server_id2.value}/{ChannelAndMessageId.backup_channel.value}/{code}')
        except (commands.CommandError, commands.BadArgument, commands.ChannelNotFound, commands.MessageNotFound, commands.ChannelNotReadable):
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
            code = await commands.MessageConverter().convert(self.ctx, f'https://discord.com/channels/{ChannelAndMessageId.server_id2.value}/{ChannelAndMessageId.backup_channel.value}/{code}')
        except (commands.CommandError, commands.BadArgument, commands.ChannelNotFound, commands.MessageNotFound, commands.ChannelNotReadable):
            return 
        await code.delete()
        return
    
    async def apply_backup(self, code:int):
        backup: Optional[discord.Attachment] = self.get_backup_data(code)
        try:
            data = await backup.read(use_cached=True)
        except (discord.HTTPException, discord.Forbidden, discord.NotFound):
            return 'Can\'t apply due to some permission error'
        data = loads(data)
        guild = self.ctx.guild
        for i in data:
            if i.lower() == 'roles':
                for j in data[i]:
                    role_in_server = await commands.RoleConverter().convert(self.ctx,j)
                    await role_in_server.edit(reason = self.reason)
    
