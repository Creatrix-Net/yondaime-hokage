import io
from typing import Optional

import discord
from discord import CategoryChannel, Role, StageChannel, TextChannel, VoiceChannel
from discord.ext.commands import Context
from orjson import dumps

from ...util.vars import ChannelAndMessageId


class BackupDatabse:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.backup_channel = ctx.get_config_channel_by_name_or_id(
            ChannelAndMessageId.backup_channel.value)

    async def create_backup(self):
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
                        "permission": {
                            "add_reactions": i.permissions.add_reactions,
                            "administrator": i.permissions.administrator,
                            "attach_files": i.permissions.attach_files,
                            "read_message_history":
                            i.permissions.read_message_history,
                            "ban_members": i.permissions.ban_members,
                            "manage_channels": i.permissions.manage_channels,
                            "change_nickname": i.permissions.change_nickname,
                            "connect": i.permissions.connect,
                            "create_instant_invite":
                            i.permissions.create_instant_invite,
                            "create_private_threads":
                            i.permissions.create_private_threads,
                            "create_public_threads":
                            i.permissions.create_public_threads,
                            "deafen_members": i.permissions.deafen_members,
                            "embed_links": i.permissions.embed_links,
                            "external_emojis": i.permissions.external_emojis,
                            "external_stickers":
                            i.permissions.external_stickers,
                            "kick_members": i.permissions.kick_members,
                            "manage_channels": i.permissions.manage_channels,
                            "manage_emojis": i.permissions.manage_emojis,
                            "manage_emojis_and_stickers":
                            i.permissions.manage_emojis_and_stickers,
                            "manage_events": i.permissions.manage_events,
                            "manage_guild": i.permissions.manage_guild,
                            "manage_messages": i.permissions.manage_messages,
                            "manage_nicknames": i.permissions.manage_nicknames,
                            "manage_permissions":
                            i.permissions.manage_permissions,
                            "manage_roles": i.permissions.manage_roles,
                            "manage_threads": i.permissions.manage_threads,
                            "manage_webhooks": i.permissions.manage_webhooks,
                            "mention_everyone": i.permissions.mention_everyone,
                            "move_members": i.permissions.move_members,
                            "mute_members": i.permissions.mute_members,
                            "priority_speaker": i.permissions.priority_speaker,
                            "read_message_history":
                            i.permissions.read_message_history,
                            "read_messages": i.permissions.read_messages,
                            "request_to_speak": i.permissions.request_to_speak,
                            "send_messages": i.permissions.send_messages,
                            "send_messages_in_threads":
                            i.permissions.send_messages_in_threads,
                            "send_tts_messages":
                            i.permissions.send_tts_messages,
                            "speak": i.permissions.speak,
                            "stream": i.permissions.stream,
                            "use_external_emojis":
                            i.permissions.use_external_emojis,
                            "use_external_stickers":
                            i.permissions.use_external_stickers,
                            "use_slash_commands":
                            i.permissions.use_slash_commands,
                            "view_guild_insights":
                            i.permissions.view_guild_insights,
                            "use_voice_activation":
                            i.permissions.use_voice_activation,
                            "value": i.permissions.value,
                            "view_audit_log": i.permissions.view_audit_log,
                            "view_channel": i.permissions.view_channel,
                        },
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

    async def get_backup_data(self, code: Optional[discord.Message]):
        return code.attachments[0] if code else None

    async def delete_backup_data(
        self,
        code: Optional[discord.Message] = None,
        guild: Optional[discord.Guild] = None,
    ):
        if code is not None:
            await code.delete()
            return
