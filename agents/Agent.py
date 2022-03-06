from abc import ABC, abstractmethod


class Agent(ABC):

    @abstractmethod
    def get_vehicle(self):
        pass

    @abstractmethod
    def get_global_plan(self):
        pass


    pass





    