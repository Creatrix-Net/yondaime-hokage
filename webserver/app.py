import os
from pathlib import Path
from threading import Thread

from aiohttp import web

BASE_DIR = Path(__file__).resolve().parent
routes = web.RouteTableDef()


@routes.get("/", allow_head=False)
async def hello(request):
    return web.FileResponse(BASE_DIR / os.path.join("templates/index.html"))


app = web.Application()
app.add_routes(routes)


def run():
    web.run_app(app)


def keep_alive():
    t = Thread(target=run)
    t.start()


if __name__ == "__main__":
    run()
