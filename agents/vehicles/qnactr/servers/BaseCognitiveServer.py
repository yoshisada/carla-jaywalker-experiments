from abc import ABC, abstractmethod

from enum import Enum

class RequestType(Enum):
    MEMORY_ACCESS = 1
    MOTOR_CONTROL = 2
    COGNITIVE_PROCESS = 3

class ServerType(Enum):
    MOTOR_CONTROL = 1
    COMPLEX_COGNITION = 2
    LONGTERM_MEMORY = 3
    pass


class BaseCognitiveServer(ABC):
    def __init__(self, queue_length=10, frequency=5):
        super().__init__()
        self.queue_length = queue_length
        self.frequency = frequency
        self.request_queue = []
        self.response_queue = []
        pass

    #  if the queue is full, the oldest request is removed
    @abstractmethod
    def add_request(self, request):
        if len(self.request_queue) > self.queue_length:
            self.request_queue.pop(0)
        self.request_queue.append(request)
        pass
    
    @abstractmethod
    def process_request(self):
        pass

    @abstractmethod
    def get_response(self):
        result = self.response_queue
        self.reset_response_queue()
        return result

    def reset_request_queue(self):
        self.request_queue = []
        pass

    def reset_response_queue(self):
        self.response_queue = []
        pass


