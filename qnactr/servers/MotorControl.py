from time import sleep
from agents.navigation.controller import VehiclePIDController

class MotorControl():
    def __init__(self, vehicle):
        # self._request = None
        self._request_process_time = 0.002
        self._name = 'Motor control'

        self._vehicle = vehicle
        self._args_lateral_dict = {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 1.0 / 20.0}
        self._args_longitudinal_dict = {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0, 'dt': 1.0 / 20.0}

        self._vehicle_controller = None

        self._updated_velocity = -999 # km/h
        self._updated_waypoint = None # vehicle front and steering direction angle
        self.init_controller()
        pass

    def update_velocity_and_waypoint(self, updated_velocity, updated_waypoint):
        # print("Placing request to ", self._name)
        self._updated_velocity = updated_velocity
        self._updated_waypoint = updated_waypoint
        pass

    def process_request(self):
        # print("Processing request: ", self._name)
        if self._updated_waypoint == None or self._updated_velocity == -999:
            print("No updated waypoint or velocity")
            return
        

        control = self._vehicle_controller.run_step(self._updated_velocity, 
                                                    self._updated_waypoint)
        sleep(self._request_process_time)
        print('applying vehicle control: ', control)
        self._vehicle.apply_control(control)
        # print("Done processing request: ", self._name)
        pass

    def read_buffer(self):
        # print("Done reading result: ", self._name)
        pass

    def init_controller(self):
        self._vehicle_controller = VehiclePIDController(vehicle=self._vehicle,
                                                        args_lateral=self._args_lateral_dict, 
                                                        args_longitudinal=self._args_longitudinal_dict,
                                                        offset=1.0,
                                                        max_throttle=0.8,
                                                        max_brake=0.4,
                                                        max_steering=0.3)

        pass