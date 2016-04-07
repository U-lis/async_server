import asyncio
from serverside.protocol import GameProtocol


class Game:
    def __init__(self, *args):
        self.client_ids = args
        self.clients = set()

        self.loop = asyncio.get_event_loop()
        self.coro = self.loop.create_server(GameProtocol, port=0)
        print(type(self.coro))
        print(dir(self.coro))
        self.server = self.loop.run_until_complete(self.coro)
        self.addr = self.server.sockets[0].getsockname()
        print(self.addr)
        #self.loop.run_forever()

    def get_host_info(self):
        return self.addr


