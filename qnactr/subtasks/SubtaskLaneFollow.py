import math
from .SubtaskThread import SubtaskThread
from time import sleep


class SubtaskLaneFollow(SubtaskThread):
    def __init__(self, subtaskName, vehicle):
        SubtaskThread.__init__(self, subtaskName, vehicle)
        self._speed = 30 # km/h
        pass
    
    def run(self, localMap):
        # vehicle_speed = self.get_speed()
        # print(f'running lane follow subtask')
        return {'velocity': self._speed}


    def get_speed(self):
    
        vel = self._vehicle.get_velocity()

        return 3.6 * math.sqrt(vel.x ** 2 + vel.y ** 2 + vel.z ** 2)
    pass

