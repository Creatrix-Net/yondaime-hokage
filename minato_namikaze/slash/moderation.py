import discord, typing
import aiohttp
import random
from lib import LinksAndVars, ErrorEmbed, SuccessEmbed, detect_bad_domains

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


class BadurlsMessageCommand(discord.MessageCommand, guild_ids=[920536143244709889], name="flagged urls"):
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


class ModerationCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.add_application_command(Badurls(self))
        self.add_application_command(BadurlsMessageCommand(self))

def setup(bot):
    bot.add_cog(ModerationCog(bot))