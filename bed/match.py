import asyncio
import json
from collections import namedtuple

from bed.match_controller import MatchController
from config import MATCH_HOST, MATCH_PORT

Client = namedtuple('Client', 'reader writer')


class MatchServer:  # BaseServer
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
        print("Peer: {}".format(peername))
        new_client = Client(reader, writer)
        self.clients[peername] = new_client

        print(self.clients.keys())

        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                msg = msg.decode('utf-8').strip()
                if not msg:
                    continue
                elif msg == 'close()':
                    print("{} Closed".format(peername))
                    del self.clients[peername]
                    writer.write_eof()
                else:
                    data = json.loads(msg)
                    cmd = data['type']
                    if cmd == 'enqueue':
                        result = self.controller.enqueue(data)
                        if result['match']:
                            self.send_to_all_clients(None, self.controller.return_structure(*result))
                    else:
                        result = self.controller.return_structure(False, tuple(), "Invalid Command")
                        writer.write(bytearray(result.encode('utf-8')))

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
        self.controller.dequeue_all()
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
