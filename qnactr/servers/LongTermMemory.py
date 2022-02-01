
from time import sleep

class LongTermMemory():
    def __init__(self) -> None:
        self._requestQueue = []
        self._queueSize = 10
        self._buffer = {}
        self._request_process_time = 0.7
        self._name = 'Long term memory'
        pass

    def place_request(self, request):
        print("Placing request to ", self._name)
        if len(self._requestQueue) < self._queueSize:
            self._requestQueue.append(request)
        else:
            self._requestQueue.pop(0) # remove the oldest request
            self._requestQueue.append(request)
        pass

    def process_request(self):
        print("Processing request: ", self._name)
        current_request = self._requestQueue[0]
        if current_request.get_request_type() == 'lane_keeping':
            self.get_lane_keeping_parameter()
        elif current_request.get_request_type() == 'lane_follow':
            self.get_lane_follow_parameter()
        sleep(self._request_process_time)
        print("Done processing request: ", self._name)
        pass

    def read_buffer(self):
        print("Reading result: ", self._name)
        return self._buffer

    def get_lane_keeping_parameter(self):
        result_dict = {'near_distance': 2.0, 'far_distance': 10.0}
        self._buffer = result_dict
        pass

    def get_lane_follow_parameter(self):
        result_dict = {'maximum_acceleration': 2.0, 
                       'desired_deceleration': 1.0,
                       'desired_velocity': 1.0,
                       'desired_thw': 1.0,
                       'minimum_distance': 1.0,
                       'acceleration_exponent': 1.0}
        self._buffer = result_dict
        pass



