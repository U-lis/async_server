import asyncio
from collections import namedtuple
from serverside import r
from serverside.func import big_function

Client = namedtuple('Client', 'reader writer')


class MatchServer:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.server = None
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(self.client_connected, '192.168.0.24', 0)
            print(self.server.sockets[0].getsockname())
        except OSError:
            self.loop.stop()

    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        client.writer.write(bytearray(msg.encode('utf-8')))
        return

    def send_to_all(self, peername, msg):
        for client_peername, client in self.clients.items():
            client.writer.write(bytearray(msg.encode('utf-8')))

    def close_clients(self):
        for peername, client in self.clients.items():
            client.writer.write_eof()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(reader, writer)
        self.clients[peername] = new_client
        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                if msg == 'close()':
                    del self.clients[peername]
                    writer.write_eof()
                else:
                    self.send_to_all(peername, msg)
            except ConnectionResetError as e:
                del self.clients[peername]
                return

    def close(self):
        self.close_clients()
        self.loop.stop()


def main():
    loop = asyncio.get_event_loop()
    server = MatchServer()
    asyncio.async(server.run_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
    finally:
        loop.stop()

if __name__ == '__main__':
    main()
