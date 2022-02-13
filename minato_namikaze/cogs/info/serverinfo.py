import discord
from discord.ext import commands
from lib import Embed, serverinfo, userinfo


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
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=await serverinfo(ctx.guild, ctx.author, self.bot))

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
        e = Embed(title=f":information_source: Banner for {ctx.guild}")
        e.set_image(url=ctx.guild.banner.with_format("png").url)
        await ctx.send(embed=e)

    @commands.command(aliases=["whois", "who", "userinfo"])
    @commands.guild_only()
    async def user(self, ctx, *, user: discord.Member = None):
        """Get user information"""
        user = user or ctx.author        
        await ctx.send(embed=await userinfo(user, ctx.guild, self.bot))


def setup(bot):
    bot.add_cog(Info(bot))
