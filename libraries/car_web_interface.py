from aiohttp import web
import aiohttp, asyncio
import data

class WebInterface:

    def __init__(self, json_function):
        self.json_function = json_function

    def get_html(self):
        with open("index.html", 'r') as f:
            return f.read()

    async def html_handler(self, request):
        return web.Response(text=self.get_html(), content_type='text/html')

    async def websocket_handler(self, request):
        print('ws connection from: ' + request.remote)
        ws = aiohttp.web.WebSocketResponse()

        await ws.prepare(request)
        
        try:
            while True:
                await ws.send_json(self.json_function())
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print("client disconnected probably")
            print(e)

        return ws

    async def run(self):
        # Setup routes
        app = web.Application()
        app.add_routes([web.get('/', self.html_handler), web.get('/ws', self.websocket_handler)])

        # .run_app is apparently just a wrapper for _run_app, which is an async function
        # so we just call that, to omit the event loop voodoo magic leading to pain and suffering
        await web._run_app(app)