

from abc import abstractmethod, ABC
import threading
from time import sleep


class SubtaskThread(threading.Thread):
    def __init__(self, subtaskName):
        threading.Thread.__init__(self)
        self.subtaskName = subtaskName
        pass
    
    @abstractmethod
    def run(self):
        pass
    pass