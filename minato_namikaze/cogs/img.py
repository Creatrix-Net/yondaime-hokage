import os
from asyncio import sleep
from io import FileIO
from typing import TYPE_CHECKING, Optional, Union

import discord
from asyncdagpi import Client, ImageFeatures
from discord.ext import commands
from minato_namikaze.lib import (
    MemberID,
    Tokens,
    among_us,
    among_us_friends,
    BASE_DIR,
    Embed,
    ErrorEmbed,
)
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from minato_namikaze.lib import Context

    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class ImageManipulation(commands.Cog, name="Image Manipulation"):
    def __init__(self, bot: "MinatoNamikazeBot"):
        self.bot: "MinatoNamikazeBot" = bot
        self.dagpi: Client = Client(Tokens.dagpi.value)
        self.description = "Some fun Image Manipulation Commands"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{FRAME WITH PICTURE}")

    @commands.command(usage="[member.mention | member.id]")
    async def wni(
        self, ctx: "Context", *, member: Optional[Union[discord.Member, MemberID]]
    ):
        """Prove that you are not sus!"""
        if member == "@everyone":
            await ctx.send(f"** {ctx.author.mention} yes yes!!! Everyone is not sus!**")
            return
        member = member or ctx.author
        desc = f"** {member.mention}  was not the imposter**"

        file = discord.File(
            fp=among_us,
            filename="wni.png",
            description=f"** {member.display_name}  was not the imposter**",
        )

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url="attachment://wni.png")
        await ctx.send(file=file, embed=embed)

    @commands.command(usage="[member.mention | member.id]")
    async def wi(
        self, ctx: "Context", *, member: Optional[Union[discord.Member, MemberID]]
    ):
        """Prove anyone that they are sus!"""
        if member == "@everyone":
            desc = f"Hmmmmmmm ** {ctx.author.mention} , Hey guys {ctx.author.mention} is the sus !!!**"
            await ctx.send(ErrorEmbed(description=desc))
            return
        member = member or ctx.author
        desc = f"** {member.mention}  is the imposter**"
        text = f"{member.display_name}  is the imposter"

        embed = ErrorEmbed(description=desc, timestamp=discord.utils.utcnow())

        img = Image.open(among_us_friends)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(
            FileIO(BASE_DIR / os.path.join("lib", "data", "arial.ttf")), 60
        )
        draw.text((250, 300), text, font=font, fill="red", align="right")
        img.save("wi.png")
        embed.set_image(url="attachment://wi.png")
        await ctx.send(file=discord.File("wi.png", description=text), embed=embed)
        await sleep(3)
        os.remove("wi.png")

    @commands.command(usage="[member.mention | member.id]")
    async def triggered(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Make anyone triggered"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.triggered(), url)
        e2file = discord.File(fp=img.image, filename=f"triggered.{img.format}")
        e = Embed(title="Here You Go! Filter used is triggered!")
        e.set_image(url=f"attachment://triggered.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(
        cooldown_after_parsing=True,
        usage="[discord.member.mention.to.send | member.id] <your.message>",
    )
    async def message(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]], *, text
    ):
        """Send a fake Discord message"""
        member = member or ctx.author

        uname = member.display_name
        text = str(text)
        pfp = str(member.display_avatar.url)
        img = await self.dagpi.image_process(
            ImageFeatures.discord(), url=pfp, username=uname, text=text
        )
        e2file = discord.File(fp=img.image, filename=f"message.{img.format}")
        e = Embed(title="Here You Go! Message Sent!")
        e.set_image(url=f"attachment://message.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(
        cooldown_after_parsing=True, usage="<member.mention, captcha.text>"
    )
    async def captcha(
        self,
        ctx: "Context",
        member: Optional[Union[discord.Member, MemberID]],
        *,
        text="Detect Face",
    ):
        """Captcha v3 Image mockup"""
        member = member or ctx.author

        text = str(text)
        textaslen = len(text)
        if textaslen > 13:
            await ctx.send("Maybe text length something smaller then 13?")
        else:
            pfp = member.display_avatar.url
            img = await self.dagpi.image_process(
                ImageFeatures.captcha(), url=pfp, text=text
            )
            e2file = discord.File(fp=img.image, filename=f"captcha.{img.format}")
            e = Embed(title="Here You Go! Another Captcha?")
            e.set_image(url=f"attachment://captcha.{img.format}")
            await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def pixel(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Pixallate your pfp"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.pixel(), url)
        e2file = discord.File(fp=img.image, filename=f"pixel.{img.format}")
        e = Embed(title="Here You Go! Filter used is pixel!")
        e.set_image(url=f"attachment://pixel.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def jail(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Jail yourself or someone"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.jail(), url=url)
        e2file = discord.File(fp=img.image, filename=f"jail.{img.format}")
        e = Embed(title="Here You Go! Filter used is jail!")
        e.set_image(url=f"attachment://jail.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def wanted(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Get yourself or someone listed in Bingo Book"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.wanted(), url)
        e2file = discord.File(fp=img.image, filename=f"wanted.{img.format}")
        e = Embed(title="Here You Go! Filter used is wanted!")
        e.set_image(url=f"attachment://wanted.{img.format}")
        await ctx.send(file=e2file, embed=e)

    @commands.command(usage="[member.mention | member.id]")
    async def rainbow(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Rainbow light effect"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.gay(), url)
        e2file = discord.File(fp=img.image, filename=f"rainbow.{img.format}")
        e = Embed(title="Here You Go! Filter used is gay!")
        e.set_image(url=f"attachment://rainbow.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def gay(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Seperate yourself/others and mark them/yourself as gay!"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.gay(), url)
        e2file = discord.File(fp=img.image, filename=f"gay.{img.format}")
        e = Embed(title="There you go gay!")
        e.set_image(url=f"attachment://gay.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def trash(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Puts trash into trashbin"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.trash(), url)
        e2file = discord.File(fp=img.image, filename=f"trash.{img.format}")
        e = Embed(title="There you go piece of Trash!")
        e.set_image(url=f"attachment://trash.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(
        aliases=["delete_trash", "dt"], usage="[member.mention | member.id]"
    )
    async def delete(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Removes trash from bin"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.delete(), url)
        e2file = discord.File(fp=img.image, filename=f"delete.{img.format}")
        e = Embed(title="There you go piece of trash removed!")
        e.set_image(url=f"attachment://delete.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def angel(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Be an Angel"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.angel(), url)
        e2file = discord.File(fp=img.image, filename=f"angel.{img.format}")
        e = Embed(title="Our dear Angel!")
        e.set_image(url=f"attachment://angel.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def satan(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Be the Devil"""
        member = member or ctx.author
        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.satan(), url)
        e2file = discord.File(fp=img.image, filename=f"satan.{img.format}")
        e = Embed(title="Satan!!!")
        e.set_image(url=f"attachment://satan.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(
        aliases=["chp", "chpaint", "charcoal_paint", "charcoalp"],
        usage="[member.mention | member.id]",
    )
    async def charcoal(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Get your pfp beautiful charcoal paint"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.charcoal(), url)
        e2file = discord.File(fp=img.image, filename=f"charcoal.{img.format}")
        e = Embed(title="There you go your lovely charcoal paintaing")
        e.set_image(url=f"attachment://charcoal.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def hitler(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Hail Hitler"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.hitler(), url)
        e2file = discord.File(fp=img.image, filename=f"hitler.{img.format}")
        e = Embed(title="Worse than Hitler!!!")
        e.set_image(url=f"attachment://hitler.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def wasted(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """GTA V wasted screen"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.wasted(), url)
        e2file = discord.File(fp=img.image, filename=f"wasted.{img.format}")
        e = Embed(title="Wasted! :skull_crossbones:")
        e.set_image(url=f"attachment://wasted.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def bomb(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Bomb someone"""
        e = Embed(title="Boooom! :skull_crossbones:")
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.bomb(), url)
        e2file = discord.File(fp=img.image, filename=f"bomb.{img.format}")
        e.set_image(url=f"attachment://bomb.{img.format}")
        await ctx.send(embed=e, file=e2file)

    @commands.command(usage="[member.mention | member.id]")
    async def pat(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Pat someone, UwU!"""
        member = member or ctx.author

        url = member.display_avatar.url
        img = await self.dagpi.image_process(ImageFeatures.petpet(), url)
        e2file = discord.File(fp=img.image, filename=f"petpet.{img.format}")
        e = Embed(title="UwU Pat!")
        e.set_image(url=f"attachment://petpet.{img.format}")
        await ctx.send(file=e2file, embed=e)

    # spank
    @commands.command(usage="[member.mention | member.id]")
    async def spank(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Spank someone"""
        member = member or ctx.author
        if member in ["@everyone", "@here"]:
            await ctx.send(
                f"** {ctx.author.mention} why would you spank @everyone? **",
                allowed_mentions=discord.AllowedMentions(everyone=False),
            )
            return
        else:
            desc = f"** {ctx.author.mention} spanks {member.mention} !!! Damm! **"
        if member == ctx.author:
            desc = f"** {ctx.author.mention} spanks themselves !!! LOL! **"

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url=await ctx.tenor("anime spank"))
        await ctx.send(embed=embed)

    # slap
    @commands.command(usage="[member.mention | member.id]")
    async def slap(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Slap someone"""
        member = member or ctx.author
        if member in ["@everyone", "@here"]:
            await ctx.send(
                f"** {ctx.author.mention} why would you slap @everyone? **",
                allowed_mentions=discord.AllowedMentions(everyone=False),
            )
            return
        else:
            desc = f"** {ctx.author.mention} slaps {member.mention} !!! Damm! **"
        if member == ctx.author:
            desc = f"** {ctx.author.mention} slaps themselves !!! LOL! **"

        url = member.display_avatar.url
        img = await self.dagpi.image_process(
            ImageFeatures.slap(),
            url2=ctx.author.display_avatar.url,
            url=url,
        )
        e2file = discord.File(fp=img.image, filename=f"slap.{img.format}")
        e = Embed(description=desc)
        e.set_image(url=f"attachment://slap.{img.format}")
        await ctx.send(embed=e, file=e2file)

    # hug
    @commands.command(usage="[member.mention | member.id]")
    async def hug(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Hug someone"""
        member = member or ctx.author
        if member in ["@everyone", "@here"]:
            await ctx.send(
                f"** {ctx.author.mention} why would you hug @everyone? **",
                allowed_mentions=discord.AllowedMentions(everyone=False),
            )
            return
        else:
            desc = f"** {ctx.author.mention} hugs {member.mention} !!! :heart: :heart: :heart: **"
        if member == ctx.author:
            desc = f"** {ctx.author.mention} hugs themselves !!! :heart: :heart: :heart: :heart: **"

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url=await ctx.get_random_image_from_tag("anime hugs"))
        await ctx.send(embed=embed)

    # poke
    @commands.command(usage="[member.mention | member.id]")
    async def poke(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Poke someone"""
        member = member or ctx.author
        if member == ctx.author:
            desc = f"** {ctx.author.mention} pokes themselves! **"
        elif member in ["@everyone", "@here"]:
            await ctx.send(
                f"** {ctx.author.mention} why would you poke @everyone? **",
                allowed_mentions=discord.AllowedMentions(everyone=False),
            )
            return
        else:
            desc = f"** {ctx.author.mention} pokes {member} !!! **"
        if member == ctx.author:
            desc = f"** {ctx.author.id} pokes themselves !!! **"

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url=await ctx.get_random_image_from_tag("anime poke"))
        await ctx.send(embed=embed)

    # high5
    @commands.command(usage="[member.mention | member.id]")
    async def high5(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Do a highfive"""
        member = member or ctx.author
        if member in ["@everyone", "@here"]:
            desc = f"**@everyone , {ctx.author.mention} high-fives **"
        else:
            desc = f"**{ctx.author.mention} high fives {member.mention} !!! **"
        if member == ctx.author:
            desc = f"**{ctx.author.mention} high-fives **"

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url=await ctx.tenor("anime highfive"))
        await ctx.send(embed=embed)

    # party
    @commands.command(usage="[member.mention | member.id]")
    async def party(
        self, ctx: "Context", member: Optional[Union[discord.Member, MemberID]]
    ):
        """Party with someone"""
        member = member or ctx.author
        if member in ["@everyone", "@here"]:
            desc = (
                f"**@everyone {ctx.author.mention} is partying!! come join them !! **"
            )
        else:
            desc = (
                f"**{ctx.author.mention} parties with {member.mention} !!! Yaay !!! **"
            )
        if member == ctx.author:
            desc = f"**{ctx.author.mention} is partying !!!**"

        embed = Embed(description=desc, timestamp=discord.utils.utcnow())
        embed.set_image(url=await ctx.tenor("anime party"))
        await ctx.send(embed=embed)


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(ImageManipulation(bot))
