import discord
from discord.ext import commands
import os
import random

#Loading the .env file to environment variables
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = 'Nzc5NTU5ODIxMTYyMzE1Nzg3.X7iTqA.PEmxShgoueoJgaE6BvQatCCT4XM' 


client = commands.Bot(command_prefix=".")

@client.event
async def on_ready():
    print("Ready man")


#### Commands ####

#Member join
@client.event
async def on_member_join(member):
    print(member)

@client.event
async def on_member_remove(member):
    print(member)


#Sends hello message when someoone says hello
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('**Hello!**')


#### Commands ####

#to find the latency
@client.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

#8ball command
@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Ask again later.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful",
        "Stoping asking me fucking studip questions !!!! I need peace bitch!"
    ]
    await ctx.send(f'**Your question**: {question}\n **Here you go my Answer** : {random.choice(responses)}')
client.run(TOKEN)