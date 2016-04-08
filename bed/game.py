import json
import asyncio
from collections import namedtuple

from bed.game_controller import GameController

Client = namedtuple('Client', 'reader writer')


class GameServer:
    def __init__(self, users):
        self.loop = asyncio.get_event_loop()
        self.server = None
        self.users = users
        self.controller = GameController()
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(self.client_connected, port=0)
        except OSError as e:
            print('ERROR: {}'.format(e))
            self.loop.stop()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(reader, writer)
        self.clients[peername] = new_client

        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                msg = msg.decode('utf-8').strip()
                if not msg:
                    continue
                elif msg == 'close()':
                    print("{} closed".format(peername))
                    del self.clients[peername]
                    writer.write_eof()
                else:
                    data = json.loads(msg)
                    if data['type'] == 'connection':
                        user_id = int(data.get('user_id', '0'))
                        if user_id not in self.users:
                            # Observer?
                            payload = self.controller.return_structure(False, None, 'Not Allowed')
                            writer.write(payload.encode('utf-8'))
                    # Do Game Logic
            except ConnectionResetError as e:
                del self.clients[peername]

