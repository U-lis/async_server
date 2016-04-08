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
            r.rpush('queue', user_id)
        except Exception as e:
            print(e)
            return False, None, 'Match Enqueue Failed'

        success, result, msg = self.find_match()
        if success:
            return self.return_structure(success, result, msg)
        else:
            '''
            send True because enqueue succeed
            send false only when enqueue failed
            '''
            return self.return_structure(True, result, msg)

    def find_match(self):
        print("len: {}".format(r.llen('queue')))
        if r.llen('queue') >= GAME_SIZE:
            match = r.lrange('queue', 0, GAME_SIZE-1)
            return True, match, ''
        else:
            return False, [], 'Match Waiting...'

    def make_match(self):
        pass

    def return_structure(self, success, result, msg):
        # structure = ['match', success, result, msg]
        structure = {'type': 'match', 'success': success,
                     'result': result, 'msg': msg}
        print(structure)
        return json.dumps(structure)
