import json

from bed.app import r
from config import GAME_SIZE


class MatchController:  # BaseController with return_structure
    def enqueue(self, data):
        print(data)
        user_id = int(data.get('user_id', '0'))
        print(user_id)
        """
        user = sess.query(User).filter_by(id=user_id).first()
        if not user:
            return False, None, 'User Not Exist'
        tier = user.tier
        r.rpush('queue_'+tier, user_id)
        """
        try:
            prev_list = r.lrange('queue', 0, -1)
            prev_list = [int(x) for x in prev_list]
            if user_id in prev_list:
                r.lrem('queue', 0, user_id)
            r.rpush('queue', user_id)
        except Exception as e:
            print(e)
            return False, None, 'Match Enqueue Failed'

        success, result, msg = self.find_match()
        if success:
            return success, result, msg
        else:
            '''
            send True because enqueue succeed
            send false only when enqueue failed
            '''
            return True, result, msg

    def dequeue_all(self):
        """Delete Redis Queue
        This function is called only when matching server is going down
        """
        r.delete('queue')

    def find_match(self):
        print("len: {}".format(r.llen('queue')))
        if r.llen('queue') >= GAME_SIZE:
            match = r.lrange('queue', 0, GAME_SIZE-1)
            match = [int(x) for x in match]
            game_server = self.make_match(match)
            return True, game_server, ''
        else:
            return False, tuple(), 'Match Waiting...'

    def make_match(self, user_list):
        print("Users for match: {}".format(user_list))
        return '192.168.0.24', 45644

    def return_structure(self, *args):
        # structure = ['match', success, result, msg]
        structure = {'type': 'match', 'success': args[0],
                     'result': args[1], 'msg': args[2]}
        print(structure)
        return json.dumps(structure)
