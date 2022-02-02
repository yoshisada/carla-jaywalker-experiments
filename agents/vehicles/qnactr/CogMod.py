

class CogModAgent():
    def __init__(self, vehicle):
        self._vehicle = vehicle
        self._world = self._vehicle.get_world()
        self._completeMap = self._world.get_map() 
    pass