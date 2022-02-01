from random import choice
from time import sleep
from .subtasks import SubtaskLaneFollow
from .subtasks import SubtaskLaneKeeping   
from .servers import LongTermMemory
from .servers import ComplexCognition
from .servers import MotorControl


class CentralExecutor():
    def __init__(self):
        self._subtaskLaneFollow = SubtaskLaneFollow("SubtaskLaneFollow")
        self._subtaskLaneKeeping = SubtaskLaneKeeping("SubtaskLaneKeeping")
        self._longTermMemory = LongTermMemory()
        self._complexCognition = ComplexCognition()
        self._motorControl = MotorControl()

        self._longTermMemoryBuffer = None
        self._complexCognitionBuffer = None
        self._motorControlBuffer = None
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
        print("Monitor is running")
        self._longTermMemoryBuffer = self._longTermMemory.read_buffer()
        self._complexCognitionBuffer = self._complexCognition.read_buffer()
        self._motorControlBuffer = self._motorControl.read_buffer()
        print("Monitor is done")
        pass

    def decisionMaking(self):
        print("Decision making is running")
        run_thread = choice(self._threadList)
        run_thread.run()
        print("Decision making is done")
        pass

    def control(self):
        print("Control is running")
        self._complexCognition.place_request('request from central executor')
        print("Control is done")
        pass

    def run(self):
        self.monitor()
        self.decisionMaking()
        self.control()
        sleep(self._executionFrequency)
        pass


