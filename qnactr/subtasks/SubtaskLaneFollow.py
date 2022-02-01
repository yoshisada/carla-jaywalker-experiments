from .SubtaskThread import SubtaskThread
from time import sleep

class SubtaskLaneFollow(SubtaskThread):
    def __init__(self, subtaskName):
        SubtaskThread.__init__(self, subtaskName)
        pass
    
    def run(self):
        print("SubtaskLaneFollow is running")
        print("lane follow halts for a second")
        sleep(1.0)
        print("SubtaskLaneFollow doing something more")
        sleep(1.0)
        print("SubtaskLaneFollow is done")
        pass
    pass