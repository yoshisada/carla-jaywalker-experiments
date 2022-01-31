from subtasks.SubtaskThread import SubtaskThread
from time import sleep

class SubtaskLaneKeeping(SubtaskThread):
    def __init__(self, subtaskName):
        SubtaskThread.__init__(self, subtaskName)
        pass
    
    def run(self):
        print("SubtaskLaneKeeping is running")
        print("SubtaskLaneKeeping halting for a second")
        sleep(1.0)
        print("SubtaskLaneKeeping doing something more and halts again")
        sleep(1.0)
        print("SubtaskLaneKeeping is done")
        pass
    pass