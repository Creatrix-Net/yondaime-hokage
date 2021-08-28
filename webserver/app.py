from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/', allow_head=False)
async def hello(request):
    return web.Response(text="Hello, world")

app = web.Application()
app.add_routes(routes)
web.run_app(app,port=80,host='127.0.0.1')