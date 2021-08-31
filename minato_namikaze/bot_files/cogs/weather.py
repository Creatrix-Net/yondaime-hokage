import datetime
from random import choice
from typing import Literal, Optional
from urllib.parse import urlencode

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands.converter import Converter
from discord.ext.commands.errors import BadArgument


class UnitConverter(Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Optional[str]:
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
            raise BadArgument("`{units}` is not a vaild option!").format(
                units=argument)
        return new_units


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        default = {"units": None}
        self.unit = {
            "imperial": {"code": ["i", "f"], "speed": "mph", "temp": " °F"},
            "metric": {"code": ["m", "c"], "speed": "km/h", "temp": " °C"},
            "kelvin": {"code": ["k", "s"], "speed": "km/h", "temp": " K"},
        }
        self.description = 'Get weather data from https://openweathermap.org'
    
    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{SUN BEHIND CLOUD}')

    @commands.group(name="weather", aliases=["we"], invoke_without_command=True)
    @commands.bot_has_permissions(embed_links=True)
    async def weather(self, ctx: commands.Context, *, location: str) -> None:
        """
        Display weather in a given location
        `location` must take the form of `city, Country Code`
        example: `)weather New York,US`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, location=location)

    @weather.command(name="zip")
    @commands.bot_has_permissions(embed_links=True)
    async def weather_by_zip(self, ctx: commands.Context, *, zipcode: str) -> None:
        """
        Display weather in a given location
        `zipcode` must be a valid ZIP code or `ZIP code, Country Code` (assumes US otherwise)
        example: `)weather zip 700082`
        """
        await ctx.trigger_typing()
        await self.get_weather(ctx, zipcode=zipcode)

    @weather.command(name="cityid")
    @commands.bot_has_permissions(embed_links=True)
    async def weather_by_cityid(self, ctx: commands.Context, *, cityid: int) -> None:
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
    async def weather_by_coordinates(self, ctx: commands.Context, lat: float, lon: float) -> None:
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
        ctx: commands.Context,
        *,
        location: Optional[str] = None,
        zipcode: Optional[str] = None,
        cityid: Optional[int] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> None:
        guild = ctx.message.guild
        author = ctx.message.author
        units = choice(["kelvin", "imperial", "metric"])
        params = {"appid": "88660f6af079866a3ef50f491082c386", "units": units}
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
        url = "https://api.openweathermap.org/data/2.5/weather?{0}".format(
            urlencode(params))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
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
        windspeed = str(data["wind"]["speed"]) + \
            " " + self.unit[units]["speed"]
        if units == "kelvin":
            currenttemp = abs(currenttemp - 273.15)
            mintemp = abs(maxtemp - 273.15)
            maxtemp = abs(maxtemp - 273.15)
        sunrise = datetime.datetime.utcfromtimestamp(
            data["sys"]["sunrise"] + data["timezone"]
        ).strftime("%H:%M")
        sunset = datetime.datetime.utcfromtimestamp(
            data["sys"]["sunset"] + data["timezone"]
        ).strftime("%H:%M")
        embed = discord.Embed(colour=discord.Colour.blue())
        if len(city) and len(country):
            embed.add_field(name="🌍 **Location**",
                            value="{0}, {1}".format(city, country))
        else:
            embed.add_field(
                name="\N{EARTH GLOBE AMERICAS} **Location**", value="*Unavailable*"
            )
        embed.add_field(
            name="\N{STRAIGHT RULER} **Lat,Long**", value="{0}, {1}".format(lat, lon)
        )
        embed.add_field(name="\N{CLOUD} **Condition**", value=condition)
        embed.add_field(
            name="\N{FACE WITH COLD SWEAT} **Humidity**", value=data["main"]["humidity"]
        )
        embed.add_field(
            name="\N{DASH SYMBOL} **Wind Speed**", value="{0}".format(windspeed))
        embed.add_field(
            name="\N{THERMOMETER} **Temperature**",
            value="{0:.2f}{1}".format(currenttemp, self.unit[units]["temp"]),
        )
        embed.add_field(
            name="\N{HIGH BRIGHTNESS SYMBOL} **Min - Max**",
            value="{0:.2f}{1} to {2:.2f}{3}".format(
                mintemp, self.unit[units]["temp"], maxtemp, self.unit[units]["temp"]
            ),
        )
        embed.add_field(
            name="\N{SUNRISE OVER MOUNTAINS} **Sunrise**", value=sunrise)
        embed.add_field(
            name="\N{SUNSET OVER BUILDINGS} **Sunset**", value=sunset)
        embed.set_footer(text="Powered by https://openweathermap.org")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Weather(bot))
