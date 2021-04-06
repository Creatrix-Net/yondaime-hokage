import random
from os.path import join
from pathlib import Path

import discord
from discord.ext import commands


class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.minato_gif = bot.minato_gif
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            img=random.choice(minato_gif)
            file = discord.File(join(minato_dir, 'minato',img), filename=img)
            await guild.system_channel.send(file=file)

            f=open(Path(__file__).resolve(strict=True).parent.parent / join('bot','welcome_message.txt'),'r')
            f1=f.read()
            await guild.system_channel.send(f1.format(guild.name, self.bot.user.mention, self.bot.user.mention, self.bot.user.mention, guild.owner.mention))

            '''
            if guild.id not in (568567800910839811 , 632908146305925129):
                await guild.system_channel.send(f'----------')
                await guild.system_channel.send('My **sleeping time** is from')
                await guild.system_channel.send('**00:00 AM IST**  to')
                await guild.system_channel.send('**07:00 AM IST**')
            '''
            
            img=random.choice(minato_gif)
            file = discord.File(join(minato_dir, 'minato',img), filename=img)
            await guild.system_channel.send(file=file)
        except: pass
        await post_guild_stats_all()

        e34= discord.Embed(title=f'{guild.name}', color= 0x2ecc71,description='Added')
        if guild.icon:
            e34.set_thumbnail(url=guild.icon_url)
        if guild.banner:
            e34.set_image(url=guild.banner_url_as(format="png"))
        c = bot.get_channel(813954921782706227)
        e34.add_field(name='**Members**',value=f'{guild.member_count} | {sum(1 for member in guild.members if member.bot)}')
        await c.send(embed=e34)

    #when bot leaves the server
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        e34= discord.Embed(title=f'{guild.name}', color= 0xe74c3c,description='Left')
        if guild.icon:
            e34.set_thumbnail(url=guild.icon_url)
        if guild.banner:
            e34.set_image(url=guild.banner_url_as(format="png"))
        c = self.bot.get_channel(813954921782706227)
        if guild.name:
            await c.send(embed=e34)
        await post_guild_stats_all()

    #ban
    @commands.Cog.listener()
    async def on_member_ban(guild, user):
        bingo = discord.utils.get(guild.categories, name="Bingo Book") if discord.utils.get(guild.categories, name="Bingo Book") else False
        if bingo:
            ban = discord.utils.get(bingo.channels, name="ban") if discord.utils.get(bingo.channels, name="ban") else False
            if ban:
                e=discord.Embed(title='**Ban**',description=f'**{user.mention}** was banned!', color=0xe74c3c)
                e.set_image(url='https://i.imgur.com/B7EAJKM.jpg')
                if user.avatar_url:
                    e.set_thumbnail(url=user.avatar_url)
                await ban.send(embed=e)

    #unban
    @commands.Cog.listener()
    async def on_member_unban(guild, user):
        bingo = discord.utils.get(guild.categories, name="Bingo Book") if discord.utils.get(guild.categories, name="Bingo Book") else False
        if bingo:
            unban = discord.utils.get(bingo.channels, name="unban") if discord.utils.get(bingo.channels, name="unban") else False
            if unban:
                e=discord.Embed(title='**Unban**',description=f'**{user.mention}** was unbanned!', color=0x2ecc71)
                e.set_image(url='https://i.imgur.com/O1Xvv7I.jpg')
                if user.avatar_url:
                    e.set_thumbnail(url=user.avatar_url)
                await unban.send(embed=e)

    #on message event
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mentioned_in(message) and message.mention_everyone is False and message.content.lower() in ('<@!779559821162315787>', '<@779559821162315787>') or message.content.lower() in ('<@!779559821162315787> prefix', '<@779559821162315787> prefix'):
            if not message.author.bot:
                await  message.channel.send('The prefix is **)** ,A full list of all commands is available by typing ```)help```')
        if message.channel.id == 814134179049635840:
            embed = message.embeds[0].to_dict()
            
            for guild in self.bot.guilds:
                n=0
                try:
                    if not guild.id == 747480356625711204: 
                        e = discord.Embed(title=embed['title'],description=embed['description'] , color= 0x2ecc71)
                        e.set_thumbnail(url='https://i.imgur.com/lwGawEv.jpeg')
                        await guild.system_channel.send(embed=e)
                except:
                    try:
                        me = self.bot.get_user(571889108046184449)
                        find_bots = sum(1 for member in guild.members if member.bot)

                        embed = discord.Embed(
                            title=f"ℹ  Failed to send the message in **{guild.name}**", description=None)

                        if guild.icon:
                            embed.set_thumbnail(url=guild.icon_url)
                        if guild.banner:
                            embed.set_image(url=guild.banner_url_as(format="png"))

                        embed.add_field(name="**Server Name**",
                                        value=guild.name, inline=True)
                        embed.add_field(name="**Server ID**", value=guild.id, inline=True)
                        embed.add_field(
                            name="**Members**", value=guild.member_count, inline=True)
                        embed.add_field(name="**Bots**", value=find_bots, inline=True)
                        embed.add_field(name="**Owner**", value=guild.owner, inline=True)
                        embed.add_field(name="**Region**", value=str(guild.region).capitalize(), inline=True)
                        await me.send(embed=embed)
                    except: print('Failed')
            me = self.bot.get_user(571889108046184449)
            me.send('Failed to send in '+n+' servers')
        try:
            if message.channel.is_news():
                await message.publish() 
        except: pass
        await self.bot.process_commands(message)
