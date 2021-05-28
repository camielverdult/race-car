from aiohttp import web
import aiohttp, asyncio, socket, json

class WebInterface:

    def __init__(self,):
        self.data = {}

        self.fps = 10

    def set_fps(self, fps):
        self.fps = fps

    def update_values(self, data):
        self.data = data

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
                # print(self.data["lines"])
                await ws.send_json(self.data)
                await asyncio.sleep(1.0/self.fps)
                
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