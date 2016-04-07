import asyncio


def watch_stdin():
    msg = input('MSG: ')
    return msg


class Client(asyncio.Protocol):
    reader = None
    writer = None
    sockname = None

    def send_msg(self, msg):
        msg += '\n'
        self.writer.write(bytearray(msg.encode('utf-8')))

    def close(self):
        mainloop = asyncio.get_event_loop()
        mainloop.stop()

    @asyncio.coroutine
    def create_input(self):
        while True:
            mainloop = asyncio.get_event_loop()
            future = mainloop.run_in_executor(None, watch_stdin)
            input_msg = yield from future
            if input_msg == 'quit' or not self.writer:
                self.close()
                break
            elif input_msg:
                mainloop.call_soon_threadsafe(self.send_msg, input_msg)

    @asyncio.coroutine
    def connect(self):
        print("Connecting...")
        try:
            reader, writer = yield from asyncio.open_connection('192.168.0.24', 12345)
            asyncio.async(self.create_input())
            self.reader = reader
            self.writer = writer
            self.sockname = writer.get_extra_info('sockname')
            while not reader.at_eof():
                msg = yield from reader.readline()
                if msg:
                    print(msg.decode('utf-8'))
            print('server closed connection')
            self.writer = None
        except ConnectionRefusedError as e:
            print("Connection Refused: {}".format(e))
            self.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    asyncio.async(asyncio.async(Client().connect()))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Get Keyboard Interrupt")
        loop.run_forever()
    loop.close()
