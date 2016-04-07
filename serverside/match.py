import asyncio
import json
from serverside import r

user_dict = {}


class MatchingProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        info = json.dumps(data)
        if info['msg'] == 'cancel':
            r.lrem('queue', 0, self.peer)
        user_id = info.get('user_id', None)
        """
        user = sess.query(User).filter_by(id=user_id).first()
        tier = user.tier
        r.rpush('queue_'+str(tier), user_id)
        user_dict[user_id] = self
        """
        r.rpush('queue', user_id)
        user_dict[user_id] = self
        matching_result = self.find_matching()
        if matching_result:
            host, port = self.make_game_server(matching_result)
            user_list = []
            for user_id in matching_result:
                user_list.append(user_dict[user_id])
            self.send_matching(user_list, host, port)

    def connection_lost(self, exc):
        r.lrem('queue', 0, self.peer)
        del user_dict[self.peer]

    def find_matching(self):
        if r.llen('queue') >= 4:
            user_list = r.lrange('queue', 0, 3)
            return user_list

    def make_game_server(self, user_id_list):
        for user_id in user_id_list:
            r.lrem('queue', user_id)
        return ('192.168.0.24', 44567)

    def send_matching(self, users, host, port):
        clients = []
        payload = json.dumps({'host':host, 'port':port})
        for user in users:
            try:
                clients.append(user_dict.pop(user))
                for client in clients:
                    client.transport.write(bytearray(payload.encode()))
            except KeyError:
                for idx, client in enumerate(clients):
                    r.lpush('queue', client)
                    user_dict[users[idx]] = client


class MatchingServer:
    pass
