from agents.vehicles import VehicleFactory
import carla
from settings import SettingsManager
from .BaseResearch import BaseResearch
from settings.circular_t_junction_settings import circular_t_junction_settings



class ResearchCogMod(BaseResearch):
    def __init__(self, client: carla.Client, logLevel, outputDir:str = "logs") -> None:
        self.name = "ResearchCogMod"
        super().__init__(name=self.name, client=client, logLevel=logLevel, outputDir=outputDir)
        
        self.settingsManager = None
        # self.pedFactory = None
        self.vehicleFactory = None
        
        self.setup()
        
        
    def destoryActors(self):
        self.logger.info('\ndestroying  walkers')
        if self.walker is not None:
            self.walker.destroy()
        self.logger.info('\ndestroying  vehicles')
        self.vehicle.destroy()
        
    def setup(self):
        self.settingsManager = SettingsManager(self.client, circular_t_junction_settings)
        # self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)
        
        self.walker = None
        self.walkerAgent = None
        self.walkerSetting = self.getWalkerSetting()
        self.walkerSpawnPoint = carla.Transform(location = self.walkerSetting.source)
        self.walkerDestination = self.walkerSetting.destination
        
        self.vehicle = None
        self.vehicleAgent = None
        self.vehicleSpawnPoint = self.settingsManager.getEgoSpawnpoint()
        
        self.simulator = None # populated when run
        
        
