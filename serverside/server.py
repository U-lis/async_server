import asyncio
from serverside.protocol import GameProtocol


def main():
    loop = asyncio.get_event_loop()
    coro = loop.create_server(GameProtocol, port=0)
    server = loop.run_until_complete(coro)
    print(server.sockets[0].getsockname())
    server.clients = set()
    loop.run_forever()
"""
import asyncio
from collections import namedtuple

Client = namedtuple('Client', 'reader writer')


class Server:
    clients = {}
    server = None

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(self.client_connected, '192.168.0.24', 0)
            addr = self.server.sockets[0].getsockname()
            print(addr)
            print("Running server on {}".format(addr))
        except OSError:
            print("ERROR")
            self.loop.stop()

    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        print("send to {}".format(peername))
        client.writer.write("{}\n".format(msg).encode('utf-8'))
        return

    def send_to_all_clients(self, peername, msg):
        print("send to all")
        for client_peername, client in self.clients.items():
            client.writer.write("{}:{}\n".format(peername, msg).encode('utf-8'))
        return

    def close_clients(self):
        print("send EOF to all clients to close")
        for peername, client in self.clients.items():
            client.writer.write_eof()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        print("client connected")
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(reader, writer)
        self.clients[peername] = new_client
        self.send_to_client(peername, "Welcome {}".format(peername))
        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                if msg:
                    msg = msg.decode().strip()
                    print("msg received: {}".format(msg))
                    if not msg == 'close()':
                        self.send_to_all_clients(peername, msg)
                else:
                    print("{} disconnected".format(peername))
                    del self.clients[peername]
                    self.send_to_all_clients(peername, 'disconnected')
                    writer.write_eof()
            except ConnectionResetError as e:
                print('ERROR: {}'.format(e))
                del self.clients[peername]
                return

    def close(self):
        self.close_clients()
        self.loop.stop()


def main():
    loop = asyncio.get_event_loop()
    server = Server()
    asyncio.async(server.run_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupt. Closing...")
        server.close()
    finally:
        loop.close()
"""