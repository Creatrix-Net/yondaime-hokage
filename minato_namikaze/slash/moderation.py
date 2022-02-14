import random
import typing
from datetime import timedelta

import aiohttp
import discord
from discord.abc import GuildChannel
from lib import (ErrorEmbed, LinksAndVars, RaidMode, SuccessEmbed,
                 antiraid_channel_name, database_category_name,
                 detect_bad_domains)


class Badurls(discord.SlashCommand, name="badurls"):
    """Check if a text has a malicious url or not from a extensive list 60k+ flagged domains"""
    name = "bad urls"

    content = discord.application_command_option(description='The text, url or a list of urls to check', type=str)
   
    @content.autocomplete
    async def content_autocomplete(self, response: discord.AutocompleteResponse) -> typing.AsyncIterator[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(LinksAndVars.bad_links.value) as resp:
                list_of_bad_domains = (await resp.text()).split('\n')
        
        end = random.randint(25, len(list_of_bad_domains))
        for domain in list_of_bad_domains[end-25:end]:
            if response.value.lower() in domain.lower():
                yield domain
    
    def __init__(self, cog):
        self.cog = cog

    async def callback(self, response: discord.SlashCommandResponse):
        detected_urls = await detect_bad_domains(response.options.content)
        if len(detected_urls) != 0:   
            embed = ErrorEmbed(title='SCAM/PHISHING/ADULT LINK(S) DETECTED')
            detected_string = '\n'.join([f'- ||{i}||' for i in set(detected_urls)])
            embed.description = f'The following scam url(s) were detected:\n{detected_string}'
            embed.set_author(name=response.interaction.user.display_name,icon_url=response.interaction.user.display_avatar.url)
            await response.send_message(embed=embed,ephemeral=True)
            return
        await response.send_message(embed=SuccessEmbed(title="The url or the text message is safe!"),ephemeral=True)


class BadurlsMessageCommand(discord.MessageCommand, name="Flagged Urls"):
    """Check if a text has a malicious url or not from a extensive list 60k+ flagged domains"""
    def __init__(self, cog):
        self.cog = cog


    async def callback(self, response: discord.MessageCommandResponse):
        message = response.target
        detected_urls = await detect_bad_domains(message.content)
        if len(detected_urls) != 0:   
            embed = ErrorEmbed(title='SCAM/PHISHING/ADULT LINK(S) DETECTED')
            detected_string = '\n'.join([f'- ||{i}||' for i in set(detected_urls)])
            embed.description = f'The following scam url(s) were detected:\n{detected_string}'
            embed.set_author(name=response.target.author.display_name,icon_url=response.target.author.display_avatar.url)
            await response.send_message(embed=embed,ephemeral=True)
            return
        await response.send_message(embed=SuccessEmbed(title="The url or the text message is safe!"),ephemeral=True)


class AntiRaid(discord.SlashCommand):
    """Enable or disable Antiraid system for the server"""
    switch: typing.Literal["on", "strict", "off"] = discord.application_command_option(description="Antiraid different modes",default="on")
    channel: typing.Optional[GuildChannel] = discord.application_command_option(channel_types=[discord.TextChannel],description="Channel to broadcast join messages", default=None)
    
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).manage_guild:
            return True
        else:
            await response.send_message("You don't have the `Manage Guild` permission", ephemeral=True)
            return False
    
    async def add_and_check_data(
        self,
        dict_to_add: dict,
        guild: discord.Guild
    ) -> None:
        database = await self.cog.bot.db.new(database_category_name,antiraid_channel_name)
        guild_dict = await database.get(guild.id)
        if guild_dict is None:
            await database.set(guild.id, dict_to_add)
            return
        guild_dict.update(dict_to_add)
        await database.set(guild.id, guild_dict)
        return
    
    async def callback(self, response: discord.SlashCommandResponse):
        database = await self.cog.bot.db.new(database_category_name,antiraid_channel_name)
        switch = response.options.switch
        if switch.lower() == "off":
            await database.delete(response.interaction.guild_id)
            try:
                await response.interaction.guild.edit(verification_level=discord.VerificationLevel.low)
                await response.send_message("Raid mode disabled. No longer broadcasting join messages.",ephemeral=True)
            except discord.HTTPException:
                await response.send_message("\N{WARNING SIGN} Could not set verification level.",ephemeral=True)
            return
        if switch.lower() == "strict":
            try:
                await response.interaction.guild.edit(verification_level=discord.VerificationLevel.high)
                update_dict = {
                    "raid_mode": RaidMode.strict.value,
                    "broadcast_channel": response.options.channel.id
                }
                await self.add_and_check_data(update_dict,response.interaction.guild)
                await response.send_message(f"Raid mode enabled. Broadcasting join messages to {response.options.channel.mention}.",ephemeral=True)
            except discord.HTTPException:
                await response.send_message("\N{WARNING SIGN} Could not set verification level.",ephemeral=True)
            return
        try:
            await response.interaction.guild.edit(verification_level=discord.VerificationLevel.medium)
            update_dict = {
                "raid_mode": RaidMode.on.value,
                "broadcast_channel": response.options.channel.id
            }
            await self.add_and_check_data(update_dict,response.interaction.guild)
            await response.send_message(f"Raid mode enabled. Broadcasting join messages to {response.options.channel.mention}.",ephemeral=True)
        except discord.HTTPException:
            await response.send_message("\N{WARNING SIGN} Could not set verification level.",ephemeral=True)


class Kick(discord.UserCommand):
    '''Kicks the user from guild'''
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).kick_members:
            return True
        else:
            await response.send_message("You don't have the `Kick Members` permission", ephemeral=True)
            return False
    
    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.kick(reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})")
            await response.send_message(f'{user} kicked :foot:', ephemeral=True)
        except discord.Forbidden or discord.HTTPException:
            await response.send_message('Something went wrong or I don\'t have the `Kick Members` permission', ephemeral=True)

class Ban(discord.UserCommand):
    '''Bans the user from guild'''
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).ban_members:
            return True
        else:
            await response.send_message("You don't have the `Ban Members` permission", ephemeral=True)
            return False
    
    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.ban(reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})")
            await response.send_message(f'{user} banned :hammer:', ephemeral=True)
        except discord.Forbidden or discord.HTTPException:
            await response.send_message('Something went wrong or I don\'t have the `Ban Members` permission', ephemeral=True)


class Mute(discord.UserCommand):
    '''Mute the user from guild for a day'''
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).timeout_members:
            return True
        else:
            await response.send_message("You don't have the `Timeout Members` permission", ephemeral=True)
            return False
    
    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.edit(timed_out_until=discord.utils.utcnow()+timedelta(days=1) ,reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})")
            await response.send_message(f'{user} muted for a day :x:', ephemeral=True)
        except discord.Forbidden or discord.HTTPException:
            await response.send_message('Something went wrong or I don\'t have the `Timeout Members` permission', ephemeral=True)


class Unmute(discord.UserCommand):
    '''Unmute the user from guild'''
    def __init__(self, cog):
        self.cog = cog
    
    async def command_check(self, response: discord.SlashCommandResponse) -> bool:
        if response.channel.permissions_for(response.user).timeout_members:
            return True
        else:
            await response.send_message("You don't have the `Timeout Members` permission", ephemeral=True)
            return False
    
    async def callback(self, response: discord.UserCommandResponse):
        user = response.target
        try:
            await user.edit(timed_out_until=discord.utils.utcnow() ,reason=f"[Context Menu Interaction] {response.interaction.user} (ID: {response.interaction.user.id})")
            await response.send_message(f'{user} unmuted :white_check_mark:', ephemeral=True)
        except discord.Forbidden or discord.HTTPException:
            await response.send_message('Something went wrong or I don\'t have the `Timeout Members` permission', ephemeral=True)


class ModerationCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Badurls(self))
        self.add_application_command(BadurlsMessageCommand(self))
        self.add_application_command(AntiRaid(self))
        self.add_application_command(Kick(self))
        self.add_application_command(Ban(self))
        self.add_application_command(Mute(self))
        self.add_application_command(Unmute(self))


def setup(bot):
    bot.add_cog(ModerationCog(bot))
