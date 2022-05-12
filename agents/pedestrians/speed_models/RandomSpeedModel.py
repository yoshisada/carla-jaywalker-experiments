from .SpeedModel import SpeedModel
from numpy import random

class RandomSpeedModel(SpeedModel):
    
    def initialize(self):
        self._desiredSpeed = self.internalFactors["desired_speed"] * (random.uniform(.2, .8, size=(1, 1)))[0][0]
        self._minSpeed = self.internalFactors["min_crossing_speed"] * 2
        self._maxSpeed = self.internalFactors["max_crossing_speed"] * 2
        pass