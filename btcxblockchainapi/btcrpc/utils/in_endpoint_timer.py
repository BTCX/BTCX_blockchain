import time
import requests
from btcrpc.utils.config_file_reader import ConfigFileReader

class InEndpointTimer(object):

    def __init__(self, currency):
        self.start_time = time.process_time()
        self.config_reader = ConfigFileReader()
        self.currency = currency
        self.extra_elapsed_time_added = 0.0


    def is_within_timelimit(self):
        elapsed_time = time.process_time() - self.start_time
        request_time_limit = self.config_reader.get_request_time_limit(self.currency)
        return elapsed_time + self.extra_elapsed_time_added > request_time_limit

    def validate_is_within_timelimit(self):
        if not self.is_within_timelimit():
            raise requests.Timeout(
                "The request total time of the request has exceeded the configured max time for requests")

    def maximize_extra_time(self):
        request_time_limit = self.config_reader.get_request_time_limit(self.currency)
        self.extra_elapsed_time_added = request_time_limit