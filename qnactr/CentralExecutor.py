from random import choice
from time import sleep
from .subtasks import SubtaskLaneFollow
from .subtasks import SubtaskLaneKeeping   
from .servers import LongTermMemory
from .servers import ComplexCognition
from .servers import MotorControl


class CentralExecutor():
    def __init__(self, vehicle):
        self._vehicle = vehicle
        self._subtaskLaneFollow = SubtaskLaneFollow("SubtaskLaneFollow", self._vehicle)
        self._subtaskLaneKeeping = SubtaskLaneKeeping("SubtaskLaneKeeping", self._vehicle)
        self._longTermMemory = LongTermMemory()
        self._complexCognition = ComplexCognition()
        self._motorControl = MotorControl(self._vehicle)

        self._longTermMemoryBuffer = None
        self._complexCognitionBuffer = None
        self._motorControlBuffer = None

        self._longTermMemoryRequest = None
        self._complexCognitionRequest = None
        self._motorRequest = {'velocity': 0, 'next_waypoint': None}

        self._localMap = None
        self._executionFrequency = 0.5

        # self.start_thread()
        self._threadList = [self._subtaskLaneFollow, self._subtaskLaneKeeping]
        pass


    def start_thread(self):
        self._subtaskLaneFollow.start()
        self._subtaskLaneKeeping.start()
        pass

    def monitor(self):
        # print("Monitor is running")
        self._longTermMemoryBuffer = self._longTermMemory.read_buffer()
        self._complexCognitionBuffer = self._complexCognition.read_buffer()
        self._motorControlBuffer = self._motorControl.read_buffer()
        # print("Monitor is done")
        pass

    def decisionMaking(self, map):
        # print("Decision making is running")
        run_thread = choice(self._threadList)
        return_dict = run_thread.run(map)
        print(f'return dict    {return_dict}')
        if 'next_waypoint' in return_dict:
            self._motorRequest['next_waypoint'] = return_dict['next_waypoint']
        if 'velocity' in return_dict:
            self._motorRequest['velocity'] = return_dict['velocity']
        print("Decision making is done")
        pass

    def control(self):
        # print("Control is running")
        self._motorControl.update_velocity_and_waypoint(self._motorRequest['velocity'], 
                                                        self._motorRequest['next_waypoint'])
        # print("Control is done")
        pass

    def tick_process_request(self):
        self._motorControl.process_request()
        pass


    def run(self, map):
        self.monitor()
        self.decisionMaking(map)
        self.control()
        sleep(self._executionFrequency)
        pass


