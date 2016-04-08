class GameController:
    def __init__(self):
        pass

    def return_structure(self, success, result, msg, **kwargs):
        payload = {'success': success, 'result': result, 'msg': msg}
        return payload
