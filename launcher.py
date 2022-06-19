import sys, os
import click
import logging
import asyncio
import importlib
import contextlib
import subprocess

from minato_namikaze import MinatoNamikazeBot, return_all_cogs, Base, Session, vars

from logging.handlers import RotatingFileHandler

import traceback

os.environ['ALEMBIC_CONFIG'] = str(vars.CONFIG_FILE)

try:
    import uvloop  # type: ignore
except ImportError:
    if sys.platform.startswith("win32") or sys.platform.startswith("cygwin"):
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


@contextlib.contextmanager
def setup_logging():
    log = logging.getLogger()

    try:
        # __enter__
        max_bytes = 32 * 1024 * 1024  # 32 MiB
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.getLogger("discord.state").addFilter(RemoveNoise())

        log.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename="minato_namikaze.log",
            encoding="utf-8",
            mode="w",
            maxBytes=max_bytes,
            backupCount=5,
        )
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dt_fmt, style="{"
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        # __exit__
        handlers = log.handlers[:]
        for hdlr in handlers:
            hdlr.close()
            log.removeHandler(hdlr)


async def run_bot():
    bot = MinatoNamikazeBot()
    await bot.start()


@click.group(invoke_without_command=True, options_metavar="[options]")
@click.pass_context
def main(ctx):
    """Launches the bot."""
    if ctx.invoked_subcommand is None:
        with setup_logging():
            asyncio.run(run_bot())


async def create_tables():
    engine = Session.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@main.group(short_help="database stuff", options_metavar="[options]")
def db():
    pass


@db.command(
    short_help="initialises the databases for the bot", options_metavar="[options]"
)
@click.argument("cogs", nargs=-1, metavar="[cogs]")
def init(cogs):
    """This manages the migrations and database creation system for you."""
    run = asyncio.get_event_loop().run_until_complete
    if not cogs:
        cogs = cogs = [
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


@db.command(short_help="upgrades from a migration")
@click.argument("cog", nargs=1, metavar="[cog]")
@click.option("-q", "--quiet", help="less verbose output", is_flag=True)
@click.option("--index", help="the index to use", default=-1)
def upgrade(cog, quiet, index):
    """Runs an upgrade from a migration"""
    run = asyncio.get_event_loop().run_until_complete


@db.command(short_help="downgrades from a migration")
@click.argument("cog", nargs=1, metavar="[cog]")
@click.option("-q", "--quiet", help="less verbose output", is_flag=True)
@click.option("--index", help="the index to use", default=-1)
def downgrade(cog, quiet, index):
    """Runs an downgrade from a migration"""
    run = asyncio.get_event_loop().run_until_complete


async def remove_databases(pool, cog, quiet):
    async with pool.acquire() as con:
        tr = con.transaction()
        await tr.start()
        # for table in Table.all_tables():
        #     try:
        #         await table.drop(verbose=not quiet, connection=con)
        #     except RuntimeError as e:
        #         click.echo(f"Could not drop {table.__tablename__}: {e}", err=True)
        #         await tr.rollback()
        #         break
        #     else:
        #         click.echo(f"Dropped {table.__tablename__}.")
        # else:
        #     await tr.commit()
        #     click.echo(f"successfully removed {cog} tables.")


@db.command(short_help="removes a cog's table", options_metavar="[options]")
@click.argument("cog", metavar="<cog>")
@click.option("-q", "--quiet", help="less verbose output", is_flag=True)
def drop(cog, quiet):
    """This removes a database and all its migrations.

    You must be pretty sure about this before you do it,
    as once you do it there's no coming back.

    Also note that the name must be the database name, not
    the cog name.
    """

    run = asyncio.get_event_loop().run_until_complete
    click.confirm("do you really want to do this?", abort=True)

    # try:
    #     pool = run(Table.create_pool(token_get("DATABASE_URL")))
    # except Exception:
    #     click.echo(
    #         f"Could not create PostgreSQL connection pool.\n{traceback.format_exc()}",
    #         err=True,
    #     )
    #     return

    # if not cog.startswith("cogs."):
    #     cog = f"cogs.{cog}"

    # try:
    #     importlib.import_module(cog)
    # except Exception:
    #     click.echo(f"Could not load {cog}.\n{traceback.format_exc()}", err=True)
    #     return

    # run(remove_databases(pool, cog, quiet))


if __name__ == "__main__":
    main()
