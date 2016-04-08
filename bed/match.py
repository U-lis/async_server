import asyncio
import json
from collections import namedtuple

from bed.match_controller import MatchController
from config import MATCH_HOST, MATCH_PORT

Client = namedtuple('Client', 'reader writer')


class MatchServer:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.server = None
        self.clients = {}
        self.controller = MatchController()

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(self.client_connected, MATCH_HOST, MATCH_PORT)
            print("Listen on {}".format(self.server.sockets[0].getsockname()))
        except OSError as e:
            print("ERROR: {}".format(e))
            self.loop.stop()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(reader, writer)
        self.clients[peername] = new_client
        print(self.clients)

        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                print(msg)
                if msg == 'close()':
                    del self.clients[peername]
                    writer.write_eof()
                else:
                    data = json.loads(msg.decode('utf-8'))
                    target_func = getattr(self.controller, data['type'])
                    self.send_to_client(peername, target_func(data))

            except ConnectionResetError as e:
                print('ConnectionError: {}'.format(e))
                del self.clients[peername]
                return
            except Exception as e:
                print(e)
                continue

    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        client.writer.write(bytearray(msg.encode('utf-8')))

    def send_to_all_clients(self, peername, msg):
        for peername, client in self.clients.items():
            client.writer.write(bytearray(msg.encode('utf-8')))

    def close(self):
        for peername, client in self.clients.items():
            client.writer.write_eof()
        self.loop.stop()


def main():
    loop = asyncio.get_event_loop()
    server = MatchServer()
    asyncio.async(server.run_server())

    try:
        loop.run_forever()
    except Exception as e:
        print('Main Excpetion:{}'.format(e))
        server.close()
    finally:
        loop.stop()

if __name__ == '__main__':
    main()
