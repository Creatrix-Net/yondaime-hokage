import discord
from discord.ext import commands
from ...lib import ChannelAndMessageId


class BackUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Create a backup for your server"
        self.backup_channel = bot.get_config_channel_by_name_or_id(ChannelAndMessageId.backup_channel.value)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f4be")
    
    @commands.command(description="Create backup of the server")
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(2,60,commands.BucketType.guild)
    async def backup(self):
        '''Create backup of the server'''
        roles_dict = {}
        async for i in ctx.guild.fetch_roles():
            if not i.managed or not i.is_integration() or not i.is_premium_subscriber():
                roles_dict.update({
                    i.name: {
                        'colour': i.colour,
                        'hoist': i.hoist,
                        'position': i.position,
                        'mentionable': i.mentionable,
                        'permission': {
                            'add_reactions': i.add_reactions,
                            'administrator': i.administrator,
                            'attach_files': i.attach_files,
                            'read_message_history': i.read_message_history,
                            'ban_members': i.ban_members,
                            'manage_channels': i.manage_channels,
                            'change_nickname': i.change_nickname,
                            'connect': i.connect,
                            'create_instant_invite': i.create_instant_invite,
                            'create_private_threads': i.create_private_threads,
                            'create_public_threads': i.create_public_threads,
                            'deafen_members': i.deafen_members,
                            'embed_links': i.embed_links,
                            'external_emojis': i.external_emojis,
                            'external_stickers': i.external_stickers,
                            'kick_members': i.kick_members,
                            'manage_channels': i.manage_channels,
                            'manage_emojis': i.manage_emojis,
                            'manage_emojis_and_stickers': i.manage_emojis_and_stickers,
                            'manage_events': i.manage_events,
                            'manage_guild': i.manage_guild,
                            'manage_messages': i.manage_messages,
                            'manage_nicknames': i.manage_nicknames,
                            'manage_permissions': i.manage_permissions,
                            'manage_roles': i.manage_roles,
                            'manage_threads': i.manage_threads,
                            'manage_webhooks': i.manage_webhooks,
                            'mention_everyone': i.mention_everyone,
                            'move_members': i.move_members,
                            'mute_members': i.mute_members,
                            'priority_speaker': i.priority_speaker,
                            'read_message_history': i.read_message_history,
                            'read_messages': i.read_messages,
                            'request_to_speak': i.request_to_speak,
                            'send_messages': i.send_messages,
                            'send_messages_in_threads': i.send_messages_in_threads,
                            'send_tts_messages': i.send_tts_messages,
                            'speak': i.speak,
                            'stream': i.stream,
                            'use_external_emojis': i.use_external_emojis,
                            'use_external_stickers': i.use_external_stickers,
                            'use_slash_commands': i.use_slash_commands,
                            'view_guild_insights': i.view_guild_insights,
                            'use_voice_activation': i.use_voice_activation,
                            'value': i.value,
                            'view_audit_log': i.view_audit_log,
                            'view_channel': i.view_channel
                        }
                    }
                })
        
        async for i in ctx.guild.fetch_channels():
            pass

def setup(bot):
    bot.add_cog(BackUp(bot))