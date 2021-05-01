from discord.ext import commands
import discord, os
import subprocess as sp
from pathlib import Path
import inspect
import textwrap
import io
import traceback
from contextlib import redirect_stdout


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.appleapiisbad = True
        self.description = 'These set of commands are only locked to the developer'
    
    def owners(ctx):
        return ctx.author.id == 571889108046184449

    @commands.group(invoke_without_command=True)
    async def dev(self, ctx, command=None):
        '''These set of commands are only locked to the developer'''
        command2 = self.bot.get_command(f"{command}")
        if command2 is None:
            await ctx.send_help(ctx.command)
        else:
            if command is None:
                await ctx.send_help(ctx.command)
            else:
                
                pass
    @dev.group(invoke_without_command=True, name='eval')
    @commands.check(owners)
    async def _eval(self, ctx, *, body):
        """Evaluates python code"""
        env = {
            'self': self,
            'ctx': ctx,
            'bot': self.bot,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource,
            'owner': self.bot.get_user(ctx.guild.owner_id) #ctx.guild.owner_id
        }

        def cleanup_code(content):
            """Automatically removes code blocks from the code."""
            # remove ```py\n```
            if content.startswith('```') and content.endswith('```'):
                return '\n'.join(content.split('\n')[1:-1])

            # remove `foo`
            return content.strip('` \n')

        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        def paginate(text: str):
            '''Simple generator that paginates text.'''
            last = 0
            pages = []
            for curr in range(0, len(text)):
                if curr % 1980 == 0:
                    pages.append(text[last:curr])
                    last = curr
                    appd_index = curr
            if appd_index != len(text)-1:
                pages.append(text[last:curr])
            return list(filter(lambda a: a != '', pages))

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await ctx.message.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    try:

                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await ctx.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await ctx.message.add_reaction('\u2705')  # tick
        elif err:
            await ctx.message.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def load(self, ctx, name: str):
        """Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"Loaded extension **`cogs/{name}.py`**")
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def reload(self, ctx, name: str):
        """Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
            await ctx.message.add_reaction('🔄')

        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def unload(self, ctx, name: str):
        """Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📤 Unloaded extension **`cogs/{name}.py`**")
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def reloadall(self, ctx):
        """Reloads all extensions. """
        
        cog_dir = Path(__file__).resolve(strict=True).parent.parent
        error_collection = []
        for file in os.listdir(cog_dir):
            if os.path.isdir(cog_dir / file):
                for i in os.listdir(cog_dir / file):
                    if i.endswith('.py'):
                        try:
                            self.bot.reload_extension(f"cogs.{file.strip(' ')}.{i[:-3]}")
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")
            else:
                if file.endswith('.py'):
                    if file != 'music1.py':
                        try:
                            self.bot.reload_extension(f'bot.cogs.{file[:-3]}')
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")

        if error_collection:
            output = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("**`Reloaded All Extentions`**")
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def sync(self, ctx):
        """Sync with GitHub and reload all the cogs"""
        embed = discord.Embed(
            title="Syncing...", description=":joy: Syncing and reloading cogs.")
        embed.set_footer(text=f"{ctx.author} | Minato Namikaze")
        msg = await ctx.send(embed=embed)
        async with ctx.channel.typing():
            output = sp.getoutput('git pull')
        embed = discord.Embed(
            title="Synced", description="Synced with GitHub and reloaded all the cogs.")
        # Reload Cogs as well
        cog_dir = Path(__file__).resolve(strict=True).parent.parent
        error_collection = []
        for file in os.listdir(cog_dir):
            if os.path.isdir(cog_dir / file):
                for i in os.listdir(cog_dir / file):
                    if i.endswith('.py'):
                        try:
                            self.bot.reload_extension(f"cogs.{file.strip(' ')}.{i[:-3]}")
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")
            else:
                if file.endswith('.py'):
                    if file != 'music1.py':
                        try:
                            self.bot.reload_extension(f'bot.cogs.{file[:-3]}')
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")

        if error_collection:
            err = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{err}"
            )

        await msg.edit(embed=embed)
    
    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def changestat(self, ctx):
        await ctx.send(f"Hi yeah")
    
    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def stream(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        await self.bot.change_presence(activity=discord.Streaming(name=activity, url="http://www.twitch.tv/transhelperdiscordbot"))
        await ctx.send(f'Changed activity to {activity} using Stream status.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def game(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        await self.bot.change_presence(activity=discord.Game(name=activity))
        await ctx.send(f'Changed activity to {activity} using Game status.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def watching(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=activity))
        await ctx.send(f'Changed activity to {activity} using Watching status.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def listening(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity))
        await ctx.send(f'Changed activity to {activity} using Listening status.')


def setup(bot):
    bot.add_cog(Developer(bot))
    