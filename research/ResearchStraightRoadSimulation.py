
import carla
from lib.MapManager import MapNames
from lib.Simulator import Simulator
from research.SimulationMode import SimulationMode
from research.BaseResearch import BaseResearch

from settings.straight_road_settings import scenario_settings
from settings import SettingsManager

from agents.vehicles import VehicleFactory

# base research class for controlloing the whole simulation

class ResearchStraightRoadSimulation(BaseResearch):
    def __init__(self, client: carla.Client, 
                 mapName,
                 logLevel, 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 simulation_id = "setting1"):

        self.name = "Research Straight Road Simulation"
        super().__init__(name=self.name, 
                         client=client, 
                         mapName=mapName, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode)

        self.simulation_id = simulation_id
        self.simulator = None

        self.settingsManager = SettingsManager(self.client, scenario_settings)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.cogmod_agent_setting = {}
        self.actor_agent_setting = {}
        self.trigger_distance = -1

        self.cogmod_agent = None
        self.actor_agent = None

        self.global_agent_list = []
        
        self.setup()
        pass


    def setup(self):
        self.settingsManager.load(self.simulation_id)
        self.cogmod_agent_setting, self.actor_agent_setting, self.trigger_distance = self.settingsManager.getStraightRoadSimulationSettings()
        self.logger.info(f'setup with trigger distance {self.trigger_distance}')
        pass

    def destoryActors(self):
        self.cogmod_agent.get_vehicle().destroy()
        self.actor_agent.get_vehicle().destroy()

        self.cogmod_agent = None
        self.actor_agent = None
        pass

    def onEnd(self):
        self.destoryActors()
        pass

    def onTick(self, world_snapshot):
        self.updateVehiclesAsynchoronousMode()
        pass

    def updateVehiclesAsynchoronousMode(self):
        if self.cogmod_agent is None or self.actor_agent is None:
            self.logger.error("cogmod agent or actor agent is None, ending simulation")
            exit()
            return
        if self.cogmod_agent.is_done() or self.actor_agent.done():
            self.destoryActors()
            self.logger.info("destory actors")
        
        cogmod_control = self.cogmod_agent.update_agent(self.global_agent_list)
        if cogmod_control is not None:
            self.cogmod_agent.vehicle.apply_control(cogmod_control)
        # print(f'vehicle at front {self.cogmod_agent.local_map.vehicle_at_front}')

        actor_control = self.actor_agent.run_step()
        if actor_control is not None:
            self.actor_agent._vehicle.apply_control(actor_control)

        pass

    def run(self, maxTicks=5000):
        self.logger.info(f'start simulation maxTicks {maxTicks}')

        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.createCogmodAgentsAsynchronousMode()
            self.createActorAgentsAsynchronousMode()
            self.world.wait_for_tick()
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.logger.warn("synchronous mode is not implemented yet")
            pass
        
        # onTickers = [self.onTick, self.printStatOnTick]
        onTickers = [self.onTick]
        onEnders = [self.onEnd]

        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks)
        pass

    def printStatOnTick(self, world_snapshot):
        actor_location = self.actor_agent.get_vehicle().get_location()
        cogmod_location = self.cogmod_agent.get_vehicle().get_location()

        actor_speed = self.actor_agent.get_vehicle().get_velocity()
        cogmod_speed = self.cogmod_agent.get_vehicle().get_velocity()

        distance = actor_location.distance(cogmod_location)
        print(f'{world_snapshot} distance {round(distance, 2)}')
        pass

    def createCogmodAgentsAsynchronousMode(self):
        spawn_transform = self.cogmod_agent_setting["spawn_transform"]
        destination_transform = self.cogmod_agent_setting["destination_transform"]
        driver_profile = self.cogmod_agent_setting["driver_profile"]

        vehicle = self.vehicleFactory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error("Could not spawn a vehicle")
            exit("cannot spawn a vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_transform.location.x, spawn_transform.location.y, spawn_transform.location.z}")
            self.logger.info(vehicle.get_control())

        self.cogmod_agent = self.vehicleFactory.createCogModAgent(1, vehicle, destination_transform, driver_profile)
        self.global_agent_list.append(self.cogmod_agent)
        pass

    def createActorAgentsAsynchronousMode(self):
        spawn_transform = self.actor_agent_setting["spawn_transform"]
        destination_transform = self.actor_agent_setting["destination_transform"]
        driver_profile = self.actor_agent_setting["driver_profile"]

        vehicle = self.vehicleFactory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error("Could not spawn a vehicle")
            exit("cannot spawn a vehicle")
        else:
            self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_transform.location.x, spawn_transform.location.y, spawn_transform.location.z}")
            self.logger.info(vehicle.get_control())

        self.actor_agent = self.vehicleFactory.createAgent(vehicle=vehicle,
                                                           target_speed=15.0)
        self.actor_agent.set_destination(destination_transform.location)

        self.global_agent_list.append(self.actor_agent)
        pass

    # def createCogmodAgentsSynchronousMode(self):
    #     spawn_transform = self.cogmod_agent_setting["spawn_transform"]
    #     destination_transform = self.cogmod_agent_setting["destination_transform"]
    #     driver_profile = self.cogmod_agent_setting["driver_profile"]

    #     spawn_command = self.vehicleFactory.spawn_command(spawn_transform)

    #     results = self.client.apply_batch_sync(spawn_command, True)

    #     if not results[0].error:
    #         vehicle = self.world.get_actor(results[0].actor_id)
    #         self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_transform.location.x, spawn_transform.location.y, spawn_transform.location.z}")


    #     pass



    