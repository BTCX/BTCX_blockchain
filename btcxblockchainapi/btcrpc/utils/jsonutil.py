import json

class JsonUtils(object):

    @classmethod
    def is_json(self, myjson):
        try:
            json_object = json.loads(myjson)
        except ValueError, e:
            return False
        return True
