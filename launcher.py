from __future__ import annotations

import asyncio
import contextlib
import importlib
import logging
import os
import subprocess
import sys
import traceback

import click
from colorama import Back
from colorama import Fore
from colorama import init  # type: ignore
from colorama import Style

from minato_namikaze import Base
from minato_namikaze import BASE_DIR
from minato_namikaze import return_all_cogs
from minato_namikaze import Session
from minato_namikaze import vars
from minato_namikaze.discordbot import MinatoNamikazeBot

# from watchfiles import run_process, DefaultFilter

init(autoreset=True)  # type: ignore

os.environ["ALEMBIC_CONFIG"] = str(vars.CONFIG_FILE)

try:
    import uvloop  # type: ignore
except ImportError:
    if sys.platform.startswith(("win32", "cygwin")):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    uvloop.install()


class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name="discord.state")

    def filter(self, record):
        if record.levelname == "WARNING" and "referencing an unknown" in record.msg:
            return False
        return True


class ColorFormatter(logging.Formatter):
    # Change this dictionary to suit your coloring needs!
    COLORS = {
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "CRITICAL": Fore.RED + Back.WHITE + Style.DIM,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        record.name = Fore.CYAN + str(record.name)
        if color:
            record.levelname = color + str(record.levelname)
            record.msg = color + str(record.msg)
        return logging.Formatter.format(self, record)


@contextlib.contextmanager
def setup_logging(log_file):
    log = logging.getLogger()
    file_or_not = (not vars.envConfig.LOCAL) or log_file
    try:
        # __enter__
        # max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        log_dir = BASE_DIR.parent / "logs"
        handler = logging.StreamHandler()
        handler.setFormatter(
            ColorFormatter(
                "[{asctime}] [{levelname}] {name}: {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            ),
        )
        if file_or_not:
            from logging.handlers import TimedRotatingFileHandler

            log_dir.mkdir(exist_ok=True)
            handler = TimedRotatingFileHandler(
                filename="logs/minato_namikaze.log",
                encoding="utf-8",
                # mode="w",
                # maxBytes=max_bytes,
                backupCount=7,
                when="midnight",
            )
            handler.setFormatter(
                logging.Formatter(
                    "[{asctime}] [{levelname}] {name}: {message}",
                    style="{",
                    datefmt="%Y-%m-%d %H:%M:%S",
                ),
            )
        log.addHandler(handler)
        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


def run_bot():
    bot = MinatoNamikazeBot()
    asyncio.run(bot.start())


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
@click.option("--log-file/--no-log-file", default=False)
def main(ctx, log_file):
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        with setup_logging(log_file):
            # run_process(BASE_DIR.parent / "minato_namikaze",target=run_bot, watch_filter=DefaultFilter(ignore_dirs=("__pycache__",)))
            run_bot()


async def create_tables():
    engine = Session.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    engine = Session.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@main.group(short_help="database stuff", options_metavar="[options]")
def db():
    pass


@db.command(
    short_help="initialises the databases for the bot",
    options_metavar="[options]",
)
@click.argument("cogs", nargs=-1, metavar="[cogs]")
def init(cogs):
    """This manages the migrations and database creation system for you."""
    run = asyncio.get_event_loop().run_until_complete
    if not cogs:
        cogs = [
            f"minato_namikaze.cogs.{e}" if not e.startswith("cogs.") else e
            for e in return_all_cogs()
        ]
    else:
        cogs = [
            f"minato_namikaze.cogs.{e}" if not e.startswith("cogs.") else e
            for e in cogs
        ]

    for ext in cogs:
        try:
            importlib.import_module(ext)
        except Exception:
            click.echo(f"Could not load {ext}.\n{traceback.format_exc()}", err=True)
            return
    run(create_tables())
    click.echo("Tables created in the database.")


@db.command(short_help="Create migrations for the databases")
@click.option("--message", prompt=True)
def makemigrations(message):
    """Update the migration file with the newest schema."""
    click.confirm("Do you want to create migrations?", abort=True)
    subprocess.run(  # skipcq: BAN-B607
        ["alembic", "revision", "--autogenerate", "-m", message],
        check=False,
    )
    click.echo("Created migrations.")


@db.command(short_help="Migrates from an migration revision")
@click.option("--upgrade/--downgrade", default=True)
@click.argument(
    "revision",
    nargs=1,
    metavar="[revision]",
    required=False,
    default="head",
)
def migrate(upgrade, revision):
    """Runs an upgrade from a migration"""
    try:
        if upgrade:
            subprocess.run(  # skipcq: BAN-B607
                ["alembic", "upgrade", revision],
                check=False,
            )
        else:
            subprocess.run(  # skipcq: BAN-B607
                [
                    "alembic",
                    "downgrade",
                    "base" if revision.lower() == "head" else revision,
                ],
                check=False,
            )
    except Exception as e:
        return


@db.command(short_help="removes a cog's table", options_metavar="[options]")
@click.argument("cogs", metavar="<cogs>", default="all")
def drop(cogs):
    """This removes a database and all its migrations.

    You must be pretty sure about this before you do it,
    as once you do it there's no coming back.

    Also note that the name must be the cog name.
    """

    run = asyncio.get_event_loop().run_until_complete
    click.confirm("Do you really want to do this?", abort=True)
    if cogs.lower() == "all":
        cogs = [
            f"minato_namikaze.cogs.{e}" if not e.startswith("cogs.") else e
            for e in return_all_cogs()
        ]
    else:
        cogs = [
            f"minato_namikaze.cogs.{e}" if not e.startswith("cogs.") else e
            for e in cogs
        ]

    for ext in cogs:
        try:
            importlib.import_module(ext)
        except Exception:
            click.echo(f"Could not load {ext}.\n{traceback.format_exc()}", err=True)
            return
    run(drop_tables())
    click.echo("Tables deleted from the database.")


if __name__ == "__main__":
    main()
