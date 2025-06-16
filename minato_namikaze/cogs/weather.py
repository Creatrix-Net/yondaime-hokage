from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands.converter import Converter
from discord.ext.commands.errors import BadArgument

from minato_namikaze.lib import Tokens

if TYPE_CHECKING:
    from minato_namikaze.lib import Context
    from .. import MinatoNamikazeBot


import logging

log = logging.getLogger(__name__)


class UnitConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> str | None:
        new_units = None
        if argument.lower() in ["f", "imperial", "mph"]:
            new_units = "imperial"
        elif argument.lower() in ["c", "metric", "kph"]:
            new_units = "metric"
        elif argument.lower() in ["k", "kelvin"]:
            new_units = "kelvin"
        elif argument.lower() in ["clear", "none"]:
            new_units = None
        else:
            raise BadArgument("`{units}` is not a vaild option!").format(units=argument)
        return new_units


class Weather(commands.Cog):
    def __init__(self, bot: MinatoNamikazeBot):
        self.bot: MinatoNamikazeBot = bot
        default = {"units": None}
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": " °F"},
            "metric": {"code": ["m", "c"], "speed": "km/h", "temp": " °C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/h", "temp": " K"},
        }
        self.description = "Get weather data from https://openweathermap.org"

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{SUN BEHIND CLOUD}")

    @commands.hybrid_group(name="weather", aliases=["we"], invoke_without_command=True)
    @commands.bot_has_permissions(embed_links=True)
    async def weather(self, ctx: Context, *, location: str) -> None:
        """
        Display weather in a given location
        `location` must take the form of `city, Country Code`
        example: `)weather New York,US`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, location=location)

    @weather.command(name="zip")
    @commands.bot_has_permissions(embed_links=True)
    async def weather_by_zip(self, ctx: Context, *, zipcode: str) -> None:
        """
        Display weather in a given location
        `zipcode` must be a valid ZIP code or `ZIP code, Country Code` (assumes US otherwise)
        example: `)weather zip 700082`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, zipcode=zipcode)

    @weather.command(name="cityid")
    @commands.bot_has_permissions(embed_links=True)
    async def weather_by_cityid(self, ctx: Context, *, cityid: int) -> None:
        """
        Display weather in a given location
        `cityid` must be a valid openweathermap city ID
        (get list here: <https://bulk.openweathermap.org/sample/city.list.json.gz>)
        example: `)weather cityid 2172797`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, cityid=cityid)

    @weather.command(name="co", aliases=["coords", "coordinates"])
    @commands.bot_has_permissions(embed_links=True)
    async def weather_by_coordinates(
        self,
        ctx: Context,
        lat: float,
        lon: float,
    ) -> None:
        """
        Display weather in a given location
        `lat` and `lon` specify a precise point on Earth using the
        geographic coordinates specified by latitude (north-south) and longitude (east-west).
        example: `)weather coordinates 35 139`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, lat=lat, lon=lon)

    async def get_weather(
        self,
        ctx: Context,
        *,
        location: str | None = None,
        zipcode: str | None = None,
        cityid: int | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> None:
        units = "metric"
        params = {"appid": Tokens.weather.value, "units": units}
        if units == "kelvin":
            params["units"] = "metric"
        if zipcode:
            params["zip"] = str(zipcode)
        elif cityid:
            params["id"] = str(cityid)
        elif lon and lat:
            params["lat"] = str(lat)
            params["lon"] = str(lon)
        else:
            params["q"] = str(location)
        url = "https://api.openweathermap.org/data/2.5/weather?{}".format(
            urlencode(params),
        )
        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            data = await resp.json()
        try:
            if data["message"] == "city not found":
                await ctx.send("City not found.")
                return
        except Exception:
            pass
        currenttemp = data["main"]["temp"]
        mintemp = data["main"]["temp_min"]
        maxtemp = data["main"]["temp_max"]
        city = data["name"]
        try:
            country = data["sys"]["country"]
        except KeyError:
            country = ""
        lat, lon = data["coord"]["lat"], data["coord"]["lon"]
        condition = ", ".join(info["main"] for info in data["weather"])
        windspeed = str(data["wind"]["speed"]) + " " + self.unit[units]["speed"]
        if units == "kelvin":
            currenttemp = abs(currenttemp - 273.15)
            mintemp = abs(maxtemp - 273.15)
            maxtemp = abs(maxtemp - 273.15)
        sunrise = datetime.datetime.utcfromtimestamp(
            data["sys"]["sunrise"] + data["timezone"],
        ).strftime("%H:%M")
        sunset = datetime.datetime.utcfromtimestamp(
            data["sys"]["sunset"] + data["timezone"],
        ).strftime("%H:%M")
        embed = discord.Embed(colour=discord.Colour.blue())
        if city and country:
            embed.add_field(
                name=":earth_africa: **Location**",
                value=f"{city}, {country}",
            )
        else:
            embed.add_field(
                name="\N{EARTH GLOBE AMERICAS} **Location**",
                value="*Unavailable*",
            )
        embed.add_field(
            name="\N{STRAIGHT RULER} **Lat,Long**",
            value=f"{lat}, {lon}",
        )
        embed.add_field(name="\N{CLOUD} **Condition**", value=condition)
        embed.add_field(
            name="\N{FACE WITH COLD SWEAT} **Humidity**",
            value=data["main"]["humidity"],
        )
        embed.add_field(
            name="\N{DASH SYMBOL} **Wind Speed**",
            value=f"{windspeed}",
        )
        embed.add_field(
            name="\N{THERMOMETER} **Temperature**",
            value="{:.2f}{}".format(currenttemp, self.unit[units]["temp"]),
        )
        embed.add_field(
            name="\N{HIGH BRIGHTNESS SYMBOL} **Min - Max**",
            value="{:.2f}{} to {:.2f}{}".format(
                mintemp,
                self.unit[units]["temp"],
                maxtemp,
                self.unit[units]["temp"],
            ),
        )
        embed.add_field(name="\N{SUNRISE OVER MOUNTAINS} **Sunrise**", value=sunrise)
        embed.add_field(name="\N{SUNSET OVER BUILDINGS} **Sunset**", value=sunset)
        embed.set_footer(text="Powered by https://openweathermap.org")
        await ctx.send(embed=embed)


async def setup(bot: MinatoNamikazeBot) -> None:
    await bot.add_cog(Weather(bot))
