import discord
from discord.ext import commands
import os

#Loading the .env file to environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = 'Nzc5NTU5ODIxMTYyMzE1Nzg3.X7iTqA.PEmxShgoueoJgaE6BvQatCCT4XM' 


client = commands.Bot(command_prefix=".d")

@client.event
async def on_ready():
    print("Ready man")

#Member join
@client.event
async def on_member_join(member):
    print(member)

@client.event
async def on_member_remove(member):
    print(member)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

@client.command
async def ping(ctx):
    await ctx.send('Pong!')

client.run(TOKEN)