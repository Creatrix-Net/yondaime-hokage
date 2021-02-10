import discord
import asyncio
from discord.ext import commands

class Help(commands.MinimalHelpCommand):
    async def send_pages(self):
        ctx = self.context
        mes = ctx.message
        for page in self.paginator.pages:
            embed = discord.Embed(description=page)
            msg = await ctx.send(embed=embed)
            
    def get_command_signature(self, command: commands.Command):
        ctx = self.context
        aliases = "|".join(command.aliases)
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        full_invoke = command.qualified_name.replace(command.name, "")
        
        prefix = ctx.prefix
        signature = f"{prefix}{full_invoke}{cmd_invoke} {command.signature}"
        return signature
    
    def get_opening_note(self):
        ctx = self.context
        return f"Thank's for using {ctx.guild.me.mention}, the list below shows all commands in their respective groups :)"

    async def command_not_found(self, command):
        destination = self.get_destination()
        embed=discord.Embed(title="Help Error", description=f"Command '{command}' Not Found!")
        await destination.send(embed=embed)
    
    async def subcommand_not_found(self, command):
        destination = self.get_destination()
        embed=discord.Embed(title="Help Error", description=f"Command '{command}' Not Found!")
        await destination.send(embed=embed)