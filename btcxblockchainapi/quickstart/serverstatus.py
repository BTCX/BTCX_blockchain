from rest_framework import serializers

class Status(object):

    def __init__(self, status="OK", message="", update=None):
        self.status = status
        self.message = message
        self.update = update

    @property
    def server_satus(self):
        return self.status

    @server_satus.setter
    def server_satus(self, value):
        self.status = value
    

    @property
    def server_message(self):
        return self.message

    @server_message.setter
    def server_message(self, value):
        self.message = value

    @property
    def server_update(self):
        return self.update

    @server_update.setter
    def server_update(self, value):
        self.update = value
    
            
    
class ServerStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=10)
    message = serializers.CharField(max_length=200)
    update = serializers.CharField(max_length=15)


class ServerStatus(object):
    def __init__(self):
        pass

    
    def do_work(self):
        status = Status(message="service is fully operational")
        status.update = "31 days"
        print(status.update)
        serializer = ServerStatusSerializer(status)
        result = serializer.data # final result
        return result

