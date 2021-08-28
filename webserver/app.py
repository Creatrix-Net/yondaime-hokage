from aiohttp import web
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
routes = web.RouteTableDef()

@routes.get('/', allow_head=False)
async def hello(request):
    return web.FileResponse(
        BASE_DIR / os.path.join('templates/index.html')
    )

app = web.Application()
app.add_routes(routes)

def run():
    web.run_app(app,port=80,host='127.0.0.1')

def keep_alive():
    t = Thread(target=run)
    t.start()