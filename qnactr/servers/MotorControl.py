from time import sleep
from agents.navigation.controller import VehiclePIDController

class MotorControl():
    def __init__(self):
        self._request = None
        self._request_process_time = 0.002
        self._name = 'Motor control'

        self._args_lateral_dict = {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 1.0 / 20.0}
        self._args_longitudinal_dict = {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0, 'dt': 1.0 / 20.0}

        self._vehicle_controller = None
        
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

    def init_controller(self):
        # self._vehicle_controller = VehiclePIDController(self._args_lateral_dict, 
        #                                                 self._args_longitudinal_dict,
        #                                                 )
        pass