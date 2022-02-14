import math
from turtle import distance
from agents.navigation.global_route_planner import GlobalRoutePlanner


class LocalMap():
    def __init__(self, vehicle, vehicle_tracking_radius=100.0):
        
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return
        self.vehicle = vehicle
        self.world = self.vehicle.get_world()
        
        self.map = self.world.get_map()
        self.vehicle_tracking_radius = vehicle_tracking_radius

        self._waypoint_tracking_radius = 1.0

        self.global_plan = None
        self.GP_sampling_resolution = 1.0 # more means less points
        self.global_planner = GlobalRoutePlanner(self.map, 
                                                 self.GP_sampling_resolution)
        
        self.cur_road_id = None
        


        self.tracked_vehicles = []
        self.tracked_traffic_signs = []

        self.vehicle_at_front = None

        # print(f'LocalMap is created with map: {self._world}')
        pass

        
    # def create_waypoint_distance_dict(self):
    #     if self.global_plan is None:
    #         raise ValueError('need to have global plan')
    #         return None
        
    #     previous_road_id = self.global_plan[-1][0].road_id
    #     sum_distance = 0.0
    #     for wp, ro in self.global_plan[::-1]: # reverse order
    #         if previous_road_id != 
            
    #         print(f'wp: {wp.id}')
    #         print(f'roadID {wp.road_id}, s {round(wp.s,2) }')
        

        
    #     pass

    def set_global_plan(self, start_transform, end_transform):
        if not start_transform or not end_transform:
            raise ValueError('need to have start and end for global plan')
            return None
        print(f'start transform: {start_transform}, \nend transform: {end_transform}')
        self.global_plan = self.global_planner.trace_route(start_transform.location, end_transform.location)

        self.cur_road_id = self.global_plan[0][0].road_id
        # creating the waypoint distance dict
        # self.create_waypoint_distance_dict()

        pass

    def get_global_plan(self):
        if self.global_plan is None:
            raise ValueError('need to have global plan')
            return None
        return self.global_plan

    # 
    def update_local_map(self):
        
        # update global plan. discarding the waypoints that are 
        # behind the vehicle's nearest waypoint's 's value' (openDrive)
        self.update_global_plan()

        # update tracked vehicles
        # self.update_tracked_vehicles()

        # # update tracked traffic signs
        # self.update_traffic_signs()

        # current_map_dict = {'route': self.global_plan,
        #                     'tracked_vehicles': self.tracked_vehicles,
        #                     'tracked_traffic_signs': self.tracked_traffic_signs}

        # return current_map_dict



    def update_traffic_signs(self):
        if len(self.tracked_traffic_signs) == 0:
            all_traffic_signs_from_world = self.world.get_actors().filter("*traffic_light*")
            self.tracked_traffic_signs = all_traffic_signs_from_world



    def update_tracked_vehicles(self):
        all_vehicle_from_world = self.world.get_actors().filter('vehicle.*')
        self.tracked_vehicles = []
        for vehicle in all_vehicle_from_world:
            distance = self.vehicle.get_location().distance(vehicle.get_location())
            if vehicle.id == self.vehicle.id or distance > self.vehicle_tracking_radius:
                continue
            else:
                self.tracked_vehicles.append(vehicle)


    def update_global_plan(self):

        # tuple_to_discard = []
        # nearest_waypoint = self.map.get_waypoint(self.vehicle.get_location())
        # for wp, ro in self.global_plan:

        tuple_to_discard = []
        nearest_waypoint = self.map.get_waypoint(self.vehicle.get_location())
        
        if nearest_waypoint.road_id != self.cur_road_id:
            for wp, ro in self.global_plan:
                if wp.road_id == self.cur_road_id:
                    tuple_to_discard.append((wp, ro))
            
            self.cur_road_id = nearest_waypoint.road_id
            

        for wp, ro in self.global_plan:
            # print(f'wp road id : {wp.road_id}, s {wp.s}, nearest {nearest_waypoint.road_id}, s {nearest_waypoint.s}')
            if wp.road_id == nearest_waypoint.road_id:
                # need this for the road direction formation according to 
                # OpenDRIVE's road direction
                if wp.lane_id < 0:
                    if wp.s <= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))
                elif wp.lane_id > 0:
                    if wp.s >= nearest_waypoint.s:
                        tuple_to_discard.append((wp, ro))

        # print(f'tuple to discard: {len(tuple_to_discard)}')

        if len(tuple_to_discard) != 0:
            for ttd in tuple_to_discard:
                self.global_plan.remove(ttd)
                pass
                
    
    def is_done(self):
        return len(self.global_plan) == 0









    # def update_global_plan(self):
    #     tuple_to_discard = []
    #     for wp, ro in self.global_plan:
    #         distance = self.vehicle.get_location().distance(wp.transform.location)
    #         # print(f'vehicle location: {self._vehicle.get_location()}')
    #         # print(f'wp: {wp.transform.location}, distance: {distance}')
    #         if distance < self._waypoint_tracking_radius:
    #             tuple_to_discard.append((wp, ro))
    #             pass
    #     if len(tuple_to_discard) != 0:
    #         for ttd in tuple_to_discard:
    #             # print(f'discarding waypoint: {ttd[0]}')
    #             self.global_plan.remove(ttd)
    #             pass
