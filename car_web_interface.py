from aiohttp import web
import aiohttp, asyncio, socket

class WebInterface:

    def __init__(self):
        self.ws = []
        self.data = {
            "distance" : 0,
            "lines" : []
        }

    def update_values(self, distance = 0, lines = []):
        self.data["distance"] = distance
        self.data["lines"] = lines

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
                await ws.send_json(self.data)
                await asyncio.sleep(0.20)
        except:
            print("client disconnected probably")

        return ws

    async def send_data(self):
        for client in self.ws:
            await client.send_json(self.data)

    async def run(self):
        # Setup routes
        app = web.Application()
        app.add_routes([web.get('/', self.html_handler), web.get('/ws', self.websocket_handler)])

        await web._run_app(app)