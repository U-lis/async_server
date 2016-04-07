import asyncio
from serverside.func import big_function
from serverside import r


class GameProtocol(asyncio.Protocol):
    def __init__(self):
        super().__init__()
        self.server = None
        self.transport = None

    def connection_made(self, transport):
        peer = transport.get_extra_info('peername')
        r.rpush('clients', peer)
        self.transport = transport
        self.server = transport._server
        self.server.clients.add(self)
        print("Connected")
        #transport.write(bytearray('Connected'.encode('utf-8')))

    def send_message(self, clients, data):
        for client in clients:
            client.transport.write(bytearray(data.encode('utf-8')))

    def data_received(self, data):
        print("Data Received")
        result = big_function(data)
        self.send_message(self.server.clients, result)

    def connection_lost(self, exc):
        try:
            self.server.clients.remove(self)
        except ValueError:
            pass
        print("Disconnected")
