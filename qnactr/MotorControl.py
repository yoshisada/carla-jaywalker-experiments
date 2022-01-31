from time import sleep

class MotorControl():
    def __init__(self) -> None:
        self._request = None
        self._request_process_time = 0.002
        self._name = 'Motor control'
        pass

    def place_request(self, request):
        print("Placing request to ", self._name)
        self._request = request
        pass

    def process_request(self):
        print("Processing request: ", self._name)
        sleep(self._request_process_time)
        print("Done processing request: ", self._name)
        pass

    def read_buffer(self):
        print("Done reading result: ", self._name)
        pass