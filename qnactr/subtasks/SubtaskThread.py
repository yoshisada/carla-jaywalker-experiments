

from abc import abstractmethod, ABC
import threading
from time import sleep


class SubtaskThread(threading.Thread):
    def __init__(self, subtaskName, vehicle):
        threading.Thread.__init__(self)
        self._subtaskName = subtaskName
        self._vehicle = vehicle
        pass
    
    @abstractmethod
    def run(self, localMap):
        pass
    pass