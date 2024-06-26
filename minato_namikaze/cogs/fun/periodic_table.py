from __future__ import annotations

import logging
from typing import List
from typing import Tuple
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands.converter import Converter
from discord.ext.commands.errors import BadArgument

from minato_namikaze.lib import EmbedPaginator
from minato_namikaze.lib import IMAGES
from minato_namikaze.lib import LATTICES
from minato_namikaze.lib import UNITS
from minato_namikaze.lib.mendeleev import element as ELEMENTS

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from lib import Context

    from ... import MinatoNamikazeBot


class ElementConverter(Converter):
    """Converts a given argument to an element object"""

    async def convert(self, ctx: "Context", argument: str) -> ELEMENTS:
        result = None
        if argument.isdigit():
            if int(argument) > 118 or int(argument) < 1:
                raise BadArgument(f"`{argument}` is not a valid element!")
            result = ELEMENTS(int(argument))
        else:
            try:
                result = ELEMENTS(argument.title())
            except Exception:
                raise BadArgument(f"`{argument}` is not a valid element!")
        if not result:
            raise BadArgument(f"`{argument}` is not a valid element!")
        return result


class MeasurementConverter(Converter):
    """Converts a given measurement type into usable strings"""

    async def convert(
        self,
        ctx: commands.Context,
        argument: str,
    ) -> list[tuple[str, str, str]]:
        result = []
        if argument.lower() in UNITS:
            result.append(
                (
                    argument.lower(),
                    UNITS[argument.lower()]["name"],
                    UNITS[argument.lower()]["units"],
                ),
            )
        else:
            for k, v in UNITS.items():
                if argument.lower() in v["name"].lower():
                    result.append((k, v["name"], v["units"]))
                elif argument.lower() in k:
                    result.append((k, v["name"], v["units"]))
        if not result:
            raise BadArgument(f"`{argument}` is not a valid measurement!")
        return result


class Elements(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        self.description = "Display information from the periodic table of elements"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{TEST TUBE}")

    @staticmethod
    def get_lattice_string(element: ELEMENTS) -> str:
        if element.lattice_structure:
            name, link = LATTICES[element.lattice_structure]
            return f"[{name}]({link})"
        return ""

    @staticmethod
    def get_xray_wavelength(element: ELEMENTS) -> str:
        try:
            ka = 1239.84 / (
                13.6057 * ((element.atomic_number - 1) ** 2) * ((1 / 1**2) - (1 / 2**2))
            )
        except Exception:
            ka = ""
        try:
            kb = 1239.84 / (
                13.6057 * ((element.atomic_number - 1) ** 2) * ((1 / 1**2) - (1 / 3**2))
            )
        except Exception:
            kb = ""
        try:
            la = 1239.84 / (
                13.6057
                * ((element.atomic_number - 7.4) ** 2)
                * ((1 / 1**2) - (1 / 2**3))
            )
        except Exception:
            la = ""
        try:
            lb = 1239.84 / (
                13.6057
                * ((element.atomic_number - 7.4) ** 2)
                * ((1 / 1**2) - (1 / 2**4))
            )
        except Exception:
            lb = ""

        data = f"Kα {ka:.2}" if ka else ""
        extra_1 = f"Kβ {kb:.2}" if kb else ""
        extra_2 = f"Lα {la:.2}" if la else ""
        extra_3 = f"Lβ {lb:.2}" if lb else ""
        return ", ".join(x for x in [data, extra_1, extra_2, extra_3] if x)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def element(
        self,
        ctx: "Context",
        element: ElementConverter,
        measurement: MeasurementConverter = None,
    ) -> None:
        """
        Display information about an element
        `element` can be the name, symbol or atomic number of the element
        `measurement` can be any of the Elements data listed here
        https://mendeleev.readthedocs.io/en/stable/data.html#electronegativities
        """
        if not measurement:
            return await ctx.send(embed=await self.element_embed(element))
        msg = f"{element.name}: "
        for m in measurement:
            extra_1 = ""
            extra_2 = ""
            data = getattr(element, m[0], "")
            if m[0] == "lattice_structure":
                extra_1, extra_2 = LATTICES[element.lattice_structure]
            if m[0] == "xrf":
                extra_2 = self.get_xray_wavelength(element)

            msg += f"{m[1]} {data} {extra_1} {extra_2} {m[2]}\n"
        await ctx.send(msg)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def elements(self, ctx: "Context", *elements: ElementConverter) -> None:
        """
        Display information about multiple elements
        `elements` can be the name, symbol or atomic number of the element
        separated by spaces
        """
        if not elements:
            elements = [ELEMENTS(e) for e in range(1, 119)]
        paginator = EmbedPaginator(
            ctx=ctx,
            entries=[await self.element_embed(e) for e in elements],
        )
        await paginator.start()

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def ptable(self, ctx: "Context") -> None:
        """Display a menu of all elements"""
        embeds = [await self.element_embed(ELEMENTS(e)) for e in range(1, 119)]
        paginator = EmbedPaginator(ctx=ctx, entries=embeds)
        await paginator.start()

    async def element_embed(self, element: ELEMENTS) -> discord.Embed:
        embed = discord.Embed()
        embed_title = (
            f"[{element.name} ({element.symbol})"
            f" - {element.atomic_number}](https://en.wikipedia.org/wiki/{element.name})"
        )
        embed.description = ("{embed_title}\n\n{desc}\n\n{sources}\n\n{uses}").format(
            embed_title=embed_title,
            desc=element.description,
            sources=element.sources,
            uses=element.uses,
        )
        if element.name in IMAGES:
            embed.set_thumbnail(url=IMAGES[element.name]["image"])
        if element.cpk_color:
            embed.colour = int(element.cpk_color.replace("#", ""), 16)
        attributes = {
            "atomic_weight": ("Atomic Weight", ""),
            "melting_point": ("Melting Point", "K"),
            "boiling_point": ("Boiling Point", "K"),
            "density": ("Density", "g/cm³"),
            "abundance_crust": ("Abundance in the Crust", "mg/kg"),
            "abundance_sea": ("Abundance in the Sea", "mg/L"),
            "name_origin": ("Name Origin", ""),
            "lattice_structure": ("Crystal Lattice", self.get_lattice_string(element)),
        }
        for attr, name in attributes.items():
            x = getattr(element, attr, "")
            if x:
                embed.add_field(name=name[0], value=f"{x} {name[1]}")
        embed.add_field(
            name="X-ray Fluorescence",
            value=self.get_xray_wavelength(element),
        )
        discovery = f"{element.discoverers} ({element.discovery_year}) in {element.discovery_location}"
        embed.add_field(name="Discovery", value=discovery)

        return embed


async def setup(bot: "MinatoNamikazeBot") -> None:
    await bot.add_cog(Elements(bot))
