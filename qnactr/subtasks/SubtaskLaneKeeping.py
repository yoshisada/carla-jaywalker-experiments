from .SubtaskThread import SubtaskThread
from time import sleep

class SubtaskLaneKeeping(SubtaskThread):
    def __init__(self, subtaskName, vehicle):
        SubtaskThread.__init__(self, subtaskName, vehicle)
        
        pass
    
    def run(self, localMap):
        global_plan = localMap['route']
        
        vehicle_location = self._vehicle.get_location()
        # print(f'current vehicle location: {vehicle_location}')
        # print(f'running lane keeping subtask')
        next_waypoint, _ = global_plan[0]
        return {'next_waypoint': next_waypoint}
        pass
    pass