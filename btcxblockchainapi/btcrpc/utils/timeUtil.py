import datetime

class TimeUtils(object):

    @classmethod
    def epoch_to_datetime(self,epochtime):
        return datetime.datetime.fromtimestamp(epochtime).strftime('%Y-%m-%d %H:%M:%S')
