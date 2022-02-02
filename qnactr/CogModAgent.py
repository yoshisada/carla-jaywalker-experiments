
import carla
import random
from qnactr.CentralExecutor import CentralExecutor
from .vision import LocalMap

class CogModAgent():
    def __init__(self, world, vehicleBP, TransformSP, TransformDes) -> None:
        self._world = world
        self._vehicleBP = vehicleBP
        self._transformSP = TransformSP
        self._transformDes = TransformDes

        self._vehicleActor = self.spawn_vehicle()

        self._centralExecutor = CentralExecutor(self._vehicleActor)
        self._localMap = LocalMap(self._world, self._vehicleActor)

        pass

    # def run(self):
    #     self._centralExecutor.run()
    #     pass

    def spawn_vehicle(self):
        if self._vehicleBP.has_attribute('color'):
            color = random.choice(self._vehicleBP.get_attribute('color').recommended_values)
            self._vehicleBP.set_attribute('color', color)
        if self._vehicleBP.has_attribute('driver_id'):
            driver_id = random.choice(self._vehicleBP.get_attribute('driver_id').recommended_values)
            self._vehicleBP.set_attribute('driver_id', driver_id)
        else:
            self._vehicleBP.set_attribute('role_name', 'autopilot')
        

        spawn_point_rotation = self._transformSP.rotation
        modified_rotation = carla.Rotation(spawn_point_rotation.pitch, spawn_point_rotation.yaw -180, spawn_point_rotation.roll)
        new_spawn_point = carla.Transform(self._transformSP.location, modified_rotation)
        vehicle = self._world.try_spawn_actor(self._vehicleBP, new_spawn_point)

        if vehicle is None:
            exit("Cannot spawn vehicle")
        else:
            print(vehicle.get_acceleration())
            print(vehicle.get_velocity())
            print(vehicle.get_location())
            print(vehicle.id)
            print(vehicle.get_velocity())    
        
        return vehicle

    def create_global_plan(self):
        self._localMap.set_global_plan(self._transformSP, self._transformDes)
        pass

    def get_global_route(self):
        return self._localMap.get_global_plan()

    def update_agent(self):
        current_map = self._localMap.update_local_map()
        self._centralExecutor.tick_process_request()
        self._centralExecutor.run(current_map)

        pass