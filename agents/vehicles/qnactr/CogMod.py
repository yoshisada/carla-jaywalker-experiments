import re
from agents.navigation.controller import VehiclePIDController
from agents.vehicles.qnactr.Request import Request
from agents.vehicles.qnactr.map.LocalMap import LocalMap
from agents.vehicles.qnactr.servers.BaseCognitiveServer import ServerType
from agents.vehicles.qnactr.servers.LongTermMemory import LongTermMemory
from agents.vehicles.qnactr.servers.ComplexCognition import ComplexCognition
from agents.vehicles.qnactr.servers.MotorControl import MotorControl
from agents.vehicles.qnactr.subtasks.LaneFollow import LaneFollow
from agents.vehicles.qnactr.subtasks.LaneKeeping import LaneKeeping, SubtaskType



class CogModAgent():
    def __init__(self, vehicle):
        if vehicle is None:
            raise ValueError('need to have vehicle')
            return
        self.vehicle = vehicle
        self.world = self.vehicle.get_world()
        self.complete_map = self.world.get_map() 

        self._destination = None
        self.local_map = LocalMap(self.vehicle)

        # cognitive servers
        self.longterm_memory = LongTermMemory(10, 1)
        self.complex_cognition = ComplexCognition(10, 1)
        self.motor_control = MotorControl(10, 1)

        self.servers = [self.longterm_memory,
                         self.complex_cognition, 
                         self.motor_control]

        # cognitive server buffers
        self.retrieval_buffer = []
        self.computation_buffer = []
        self.motor_buffer = []

        # container for requests from different subtasks to be sent to cognitive servers
        # once sent, the request is removed from the container
        self.request_queue = []
        
        # initializing controller with PID parameters for applying vehicle control
        self.init_controller()

        # creating subtasks
        self.lane_keeping_task = LaneKeeping(self.local_map)
        self.lane_following_task = LaneFollow(self.local_map)


        self.subtasks_queue = [self.lane_keeping_task, self.lane_following_task]


    def init_controller(self):
        self._args_lateral_dict = {'K_P': 1.95, 'K_I': 0.05, 'K_D': 0.2, 'dt': 0.05}
        self._args_longitudinal_dict = {'K_P': 1.0, 'K_I': 0.05, 'K_D': 0, 'dt': 0.05}
        self._max_throt = 0.75
        self._max_brake = 0.3
        self._max_steer = 0.8
        self._offset = 0

        self._vehicle_controller = VehiclePIDController(self.vehicle,
                                                        args_lateral=self._args_lateral_dict,
                                                        args_longitudinal=self._args_longitudinal_dict,
                                                        offset=self._offset,
                                                        max_throttle=self._max_throt,
                                                        max_brake=self._max_brake,
                                                        max_steering=self._max_steer)

        
    pass

    # at each step, the agent will:
    # 1. update the local map
    # 2. process requests from subtasks
    # 3. get response from the cognitive servers (long term memory, complex cognition, motor control)
    # 4. send ping to subtasks with the updated information from the buffers. (creates requests to servers)
    # 5. process requests from the subtasks

    def update_agent(self):
        # updating the local map with the current vehicle position
        # calls the update function of the local map 
        self.update_local_map()

        # calls the process_request function of the cognitive servers 
        self.process_request()

        # if any processing is done, the buffers will be updated with
        # the response from the servers. we read the buffers and store 
        # the responses in three separate buffers locally
        response_queue = self.get_response_from_buffers()
        


        # get all response for lane keeping subtask
        response_lane_keeping = []
        response_lane_following = []

        for response in response_queue:
            if response.receiver == SubtaskType.LANEKEEPING:
                response_lane_keeping.append(response)
            if response.receiver == SubtaskType.LANEFOLLOWING:
                response_lane_following.append(response)


        # self.lane_keeping_task.onTick(self.local_map, response_lane_keeping)
        self.lane_following_task.onTick(self.local_map, response_lane_following)
        
        # get all response for lane keeping subtask
        subtask_requests = self.get_request_from_subtasks()

        self.send_request_to_servers(subtask_requests)

        # print(f'target velocity {self.motor_control.target_velocity}')
        # # run one step of control using vehiclePIDController
        # if self.motor_control.target_waypoint is not None:
        #     control = self._vehicle_controller.run_step(target_speed=10, 
        #                                                 waypoint=self.motor_control.target_waypoint)
        #     self.vehicle.apply_control(control)

        req = Request(None, None, {'far_distance': 20, 'local_map': self.local_map})
        # print(f'request {req}')
        next_waypoint = self.complex_cognition.get_next_waypoint(req)
        if self.motor_control.target_velocity  != -1:
            control = self._vehicle_controller.run_step(target_speed=self.motor_control.target_velocity,
                                                        waypoint=next_waypoint)
            self.vehicle.apply_control(control)

    def get_response_from_buffers(self):

        self.retrieval_buffer = self.longterm_memory.get_response()
        self.computation_buffer = self.complex_cognition.get_response()
        self.motor_buffer = self.motor_control.get_response()

        response_queue = self.get_responses_from_buffers()
        return response_queue

    def get_responses_from_buffers(self):
        response_queue = []
        if self.retrieval_buffer:
            for response in self.retrieval_buffer:
                response_queue.append(response)
        if self.computation_buffer:
            for response in self.computation_buffer:
                response_queue.append(response)
        if self.motor_buffer:
            for response in self.motor_buffer:
                response_queue.append(response)
        return response_queue




    # distribute the request to servers 
    def send_request_to_servers(self, subtask_requests):
        for request in subtask_requests:
            if request.receiver == ServerType.LONGTERM_MEMORY:
                self.longterm_memory.add_request(request)
            if request.receiver == ServerType.COMPLEX_COGNITION:
                self.complex_cognition.add_request(request)
            if request.receiver == ServerType.MOTOR_CONTROL:
                self.motor_control.add_request(request)


    # get requests from all the subtasks
    def get_request_from_subtasks(self):

        # get all requests from subtasks
        ret = []
        for subtask in self.subtasks_queue:
            req = subtask.get_request()
            for request in req:
                ret.append(request)
        return ret


    def get_vehicle_control(self):
        return self.vehicle.get_control()

    def set_destination(self, destination):
        self._destination = destination
        self.local_map.set_global_plan(self.vehicle.get_transform(), self._destination)
        pass

    def process_request(self):
        for server in self.servers:
            server.process_request()
        pass


    def send_requests(self):
        for request in self.request_queue:
            if request.receiver == ServerType.LONGTERM_MEMORY:
                self.longterm_memory.add_request(request)
            if request.receiver == ServerType.COMPLEX_COGNITION:
                self.complex_cognition.add_request(request)
            if request.receiver == ServerType.MOTOR_CONTROL:
                self.motor_control.add_request(request)

        self.reset_request_queue()
        pass

    def reset_request_queue(self):
        self.request_queue = []
        pass
    
    
    def update_local_map(self):
        self.local_map.update_local_map()
        pass

    def destroy(self):
        self.vehicle.destroy()
        pass

    def is_done(self):
        return self.local_map.is_done()



    

    