# Discord Imports
import datetime
import re
import time
from datetime import timezone

import discord
from discord import Spotify
from discord.ext import commands

from ...lib import Embed, filter_invites


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = bot.start_time
        self.bot.github = bot.github

        self.description = "Get's the Information about the server"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{INFORMATION SOURCE}")

    @commands.command(
        name="serverdump",
        description="Sends info to my developer that you have added me",
    )
    @commands.cooldown(1, 1080, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def serverdump(self, ctx):
        """Dumps server name to the developer"""
        c = (self.bot.get_channel(813954921782706227) if not self.bot.local
             else self.bot.get_channel(869238107524968479))
        if ctx.guild.id in (747480356625711204, 869085099470225508):
            b = await ctx.send("** Okay updating info ! **")
            n = 1
            for guild in ctx.bot.guilds:
                e = discord.Embed(
                    title=f"In **{guild.name}**",
                    description="Was added",
                    color=discord.Color.green(),
                )
                if guild.icon:
                    e.set_thumbnail(url=guild.icon.url)
                if guild.banner:
                    e.set_image(url=guild.banner.with_format("png").url)
                n += 1
                e.add_field(name="**Total Members**", value=guild.member_count)
                e.add_field(
                    name="**Bots**",
                    value=sum(1 for member in guild.members if member.bot),
                )
                e.add_field(name="**Region**",
                            value=str(guild.region).capitalize(),
                            inline=True)
                e.add_field(name="**Server ID**", value=guild.id, inline=True)
                await c.send(embed=e)
            await c.send(f"In total {n} servers")
            await ctx.send(
                "**Updated ! Please check the <#813954921782706227>**")
        else:
            a = await ctx.send("**Sending the info to my developer**")
            e = discord.Embed(
                title=f"In **{ctx.guild.name}**",
                description=f"Bumped by **{ctx.message.author}**",
                color=0x2ECC71,
            )
            if ctx.guild.icon:
                e.set_thumbnail(url=ctx.guild.icon.url)
            if ctx.guild.banner:
                e.set_image(url=ctx.guild.banner.with_format("png").url)
            e.add_field(name="**Total Members**", value=ctx.guild.member_count)
            e.add_field(
                name="**Bots**",
                value=sum(1 for member in ctx.guild.members if member.bot),
            )
            e.add_field(name="**Region**",
                        value=str(ctx.guild.region).capitalize(),
                        inline=True)
            e.add_field(name="**Server ID**", value=ctx.guild.id, inline=True)
            await c.send(embed=e)
            await ctx.send(
                f'Sent the info to developer that "**I am in __{ctx.guild.name}__ guild**" , {ctx.author.mention} 😉'
            )

    """
    @commands.command()
    async def spotify(self, ctx, user: discord.Member=None):
        if user is None:
            user = ctx.author 
        for activity in user.activities:
            if isinstance(activity, Spotify):
                w = discord.Embed(title="Oooo, what a party!", description=f"{user.name} is listening to Spotify, let's see what!")
                w.add_field(name="**Listening to**", value=f"{activity.title}")
                w.add_field(name="**By**", value=f"{activity.artist}")
                w.set_thumbnail(url=activity.album_cover_url)
                return await ctx.send(embed=w)
            else:
                e = discord.Embed(title="❌ Nope, the user (you or another) aren't listening to Spotify", description=f"User {user.name} isn't listening to Spotify")
                return await ctx.send(embed=e)
    """

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """Get the avatar of you or someone else"""
        user = user or ctx.author
        e = discord.Embed(title=f"Avatar for {user.name}")
        e.set_image(url=user.avatar.url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: discord.Member = None):
        """Check when a user joined the current server"""
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=f"**{user}**",
            description=f"{user} joined **{ctx.guild.name}** at \n{user.joined_at}",
        )
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.group(aliases=["serverinfo"])
    @commands.guild_only()
    async def server(self, ctx):
        """Check info about current server"""
        guild = ctx.guild
        levels = {
            "None - No criteria set.":
            discord.VerificationLevel.none,
            "Low - Member must have a verified email on their Discord account.":
            discord.VerificationLevel.low,
            "Medium - Member must have a verified email and be registered on Discord for more than five minutes.":
            discord.VerificationLevel.medium,
            "High - Member must have a verified email, be registered on Discord for more than five minutes, and be a member of the guild itself for more than ten minutes.":
            discord.VerificationLevel.high,
            "Extreme - Member must have a verified phone on their Discord account.":
            discord.VerificationLevel.highest,
        }
        filters = {
            "Disabled - The guild does not have the content filter enabled.":
            discord.ContentFilter.disabled,
            "No Role - The guild has the content filter enabled for members without a role.":
            discord.ContentFilter.no_role,
            "All Members - The guild has the content filter enabled for every member.":
            discord.ContentFilter.all_members,
        }
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed(
                title=f"Server: __{ctx.guild.name}__ Info",
                color=ctx.author.top_role.color,
                description=f"🆔 Server ID: `{ctx.guild.id}`",
            )

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.with_format("png").url)

            verif_lvl = "None"
            for text, dvl in levels.items():
                if dvl is guild.verification_level:
                    verif_lvl = text
            for response, filt in filters.items():
                if filt is guild.explicit_content_filter:
                    content_fiter = response
            embed.add_field(name="<:ServerOwner:864765886916067359> Owner",
                            value=ctx.guild.owner)
            embed.add_field(name="🌍 Region",
                            value=str(ctx.guild.region).capitalize())
            embed.add_field(name="✔️ Verification Level", value=verif_lvl)
            embed.add_field(name="⚠️ Content Filter", value=content_filter)
            embed.add_field(name="👥 Members", value=ctx.guild.member_count)
            embed.add_field(name="🤖 Bots", value=find_bots)
            embed.add_field(name=f"🎭 Roles", value=f"{len(ctx.guild.roles)}")
            embed.add_field(
                name=f"⭐ Emotes",
                value=f"{len(ctx.guild.emojis)}/{ctx.guild.emoji_limit}",
            )

            date = ctx.guild.created_at.timestamp()
            embed.add_field(name=f"📆 Created On", value=f"<t:{round(date)}:D>")
            await ctx.send(embed=embed)

    @server.command(name="server_icon", aliases=["icon"])
    @commands.guild_only()
    async def server_icon(self, ctx):
        """Get the current server icon"""
        if not ctx.guild.icon:
            return await ctx.send("This server does not have a avatar...")
        await ctx.send(
            f"Avatar of **{ctx.guild.name}**\n{ctx.guild.icon.with_size(1024).url}"
        )

    @server.command(name="banner")
    @commands.guild_only()
    async def server_banner(self, ctx):
        """Get the current banner image"""
        if not ctx.guild.banner:
            return await ctx.send("This server does not have a banner...")
        e = Embed(title=f"ℹ Banner for {ctx.guild}")
        e.set_image(url=ctx.guild.banner.with_format("png").url)
        await ctx.send(embed=e)

    @commands.command(aliases=["whois", "who", "userinfo"])
    @commands.guild_only()
    async def user(self, ctx, *, user: discord.Member = None):
        """Get user information"""
        user = user or ctx.author
        names, nicks = await self.get_names_and_nicks(user)
        """Timestamp stuff"""
        dt = user.joined_at
        dt1 = user.created_at
        unix_ts_utc = dt.replace(tzinfo=timezone.utc).timestamp()
        unix_ts_utc1 = dt1.replace(tzinfo=timezone.utc).timestamp()
        user_c_converter = int(unix_ts_utc1)
        user_j_converter = int(unix_ts_utc)

        since_created = "<t:{}:R>".format(user_c_converter)
        if user.joined_at is not None:
            since_joined = "<t:{}:R>".format(user_j_converter)
            user_joined = "<t:{}:D>".format(user_j_converter)
        else:
            since_joined = "?"
            user_joined = "Unknown"
        user_created = "<t:{}:D>".format(user_c_converter)
        created_on = ("{} - ({})").format(since_created, user_created)
        joined_on = ("{} - ({})\n").format(since_joined, user_joined)
        """ to fetch user (for banner)"""
        uuser = await self.bot.fetch_user(user.id)
        """ to get status of user with emoji """
        status = ""
        s = user.status
        if s == discord.Status.online:
            status += "<:online:885521973965357066>"
        if s == discord.Status.offline:
            status += "<:offline:885522151866777641>"
        if s == discord.Status.idle:
            status += "<:idle:885522083545772032>"
        if s == discord.Status.dnd:
            status += "<:dnd:885522031536394320>"

        show_roles = (", ".join([
            f"<@&{x.id}>"
            for x in sorted(user.roles, key=lambda x: x.position, reverse=True)
            if x.id != ctx.guild.default_role.id
        ]) if len(user.roles) > 1 else "None")

        embed = discord.Embed(
            title=f"{status} {user.display_name}'s Info.",
            colour=user.top_role.colour.value,
            description=f"🆔 User ID: `{user.id}`",
        )
        embed.set_thumbnail(url=user.avatar.url)

        embed.add_field(name="🔹 User", value=user, inline=True)

        if names:
            name_name = ("**Previous Names:**"
                         if len(names) > 1 else "**Previous Name:**")
            name_val = filter_invites(", ".join(names))
            prev_names_val = "{}\n{}".format(
                name_name,
                name_val,
            )

        else:
            prev_names_val = ""

        if nicks:
            nick_name = ("**Previous Nicknames:**"
                         if len(nicks) > 1 else "**Previous Nickname:**")
            nick_val = filter_invites(", ".join(nicks))
            prev_nicks_val = "{}\n{}\n".format(
                nick_name,
                nick_val,
            )

        else:
            prev_nicks_val = ""

        embed.add_field(
            name="**__User info__**",
            value=("🔸 Roles: {}\n"
                   "📅 Joined On {}"
                   "{}").format(show_roles, joined_on, prev_nicks_val),
        )
        embed.add_field(
            name="**__Member Info__**",
            value=("✏️ Name: {}\n"
                   "{}: {}\n"
                   "📅 Created On: {}").format(user.display_name, user.display_name,
                                              prev_names_val, created_on),
        )

        # embed.add_field(name="✏️ Name", value=user.display_name)

        # embed.add_field(name=name_name, value=name_val)

        # embed.add_field(name="🔸 Roles", value=show_roles, inline=False)

        # embed.add_field(name="📅 Joined On", value=joined_on)

        # embed.add_field(name=f"📅 Created On", value=created_on)

        if uuser.banner:
            embed.set_image(url=uuser.banner)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
