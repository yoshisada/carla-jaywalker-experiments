from time import sleep

class ComplexCognition():
    def __init__(self) -> None:
        self._requestQueue = []
        self._queueSize = 10
        self._buffer = {}
        self._request_process_time = 0.1
        self._name = 'Complex cognition'
        pass

    def place_request(self, request):
        # print("Placing request to ", self._name)
        if len(self._requestQueue) < self._queueSize:
            self._requestQueue.append(request)
        else:
            self._requestQueue.pop(0) # remove the oldest request
            self._requestQueue.append(request)
        pass

    def process_request(self):
        current_request = self._requestQueue[0]
        if current_request.get_request_type() == 'lane_keeping':
            self.calc_lane_keeping(current_request)
        elif current_request.get_request_type() == 'lane_follow':
            self.calc_lane_follow(current_request)
        pass

    def read_buffer(self):
        # print("Reading result: ", self._name)
        return self._buffer

    def calc_lane_keeping(self, request):
        # print("Calculating lane keeping")
        pass

    def calc_lane_follow(self, request):
        # print("Calculating lane follow")
        pass