import math
import time
from unittest import result
import carla

from lib.MapManager import MapNames

from .BaseResearch import BaseResearch
from settings.t_junction_settings import t_junction_settings
from settings import SettingsManager
from agents.pedestrians import PedestrianFactory
from agents.vehicles import VehicleFactory
from lib import Simulator
from lib import Utils
from .SimulationMode import SimulationMode

class ResearchCogMod(BaseResearch):

    def __init__(self, client: carla.Client, 
                 logLevel, 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 simulation_id = "setting1"):
        self.name = "Research CogMod"
        super().__init__(name=self.name, 
                         client=client, 
                         mapName=MapNames.t_junction, 
                         logLevel=logLevel, 
                         outputDir=outputDir,
                         simulationMode=simulationMode)

        self.simulation_id = simulation_id

        self.settingsManager = SettingsManager(self.client, t_junction_settings)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.number_of_agents = 0

        self.vehicle_list = []
        self.vehicle_agent_list = []
        self.agent_parameter_list = []
        
        self.setup()


    def setup(self):
        self.settingsManager.load(self.simulation_id)
        self.simulator = None # populated when run
        self.number_of_agents, self.agent_parameter_list = self.settingsManager.getNumberOfAgentsWithParameters()
        pass




    def createVehicleAsynchoronousMode(self):       

        for i in range(self.number_of_agents):
            spawn_point = self.agent_parameter_list[i]['spawn_point']
            destination_point = self.agent_parameter_list[i]['destination_point']
            driver_profile = self.agent_parameter_list[i]['driver_profile']
           
            # spawn the vehicle in the simulator
            vehicle = self.vehicleFactory.spawn(spawn_point)
            if vehicle is None:
                self.logger.error("Could not spawn a vehicle")
                exit("cannot spawn a vehicle")
                return
            else:
                self.logger.info(f"successfully spawn vehicle {vehicle.id} at {spawn_point.location.x, spawn_point.location.y, spawn_point.location.z}")
            

            self.vehicle_list.append(vehicle)

            # create the vehicle agent
            vehicleAgent = self.vehicleFactory.createCogModAgent(id=i,
                                                                 vehicle=vehicle,
                                                                 destinationPoint=destination_point,
                                                                 driver_profile=driver_profile)
                                                                 
            self.vehicle_agent_list.append(vehicleAgent)
            pass

        pass

    def createVehicleSynchoronousMode(self):       
        batch = []
        for i in range(self.number_of_agents):
            spawn_point = self.agent_parameter_list[i]['spawn_point']
            # destination_point = self.agent_parameter_list[i]['destination_point']
            # driver_profile = self.agent_parameter_list[i]['driver_profile']

            # spawn the vehicle in the simulator
            spawn_command = self.vehicleFactory.spawn_command(spawn_point)
            batch.append(spawn_command)
            pass

        results = self.client.apply_batch_sync(batch, True)
        print(f'results : {results}')
        for i in range(len(results)):
            if results[i].error:
                exit(f"failed to spawn vehicle {i}")
                return
            else:
                print(f"successfully spawn vehicle {results[i].actor_id}")
                vehicle_actor = self.world.get_actor(results[i].actor_id)
                self.vehicle_list.append(vehicle_actor)
                vehicleAgent = self.vehicleFactory.createCogModAgent(id=vehicle_actor.id,
                                                                     vehicle=vehicle_actor,
                                                                     destinationPoint=self.agent_parameter_list[i]['destination_point'],
                                                                     driver_profile=self.agent_parameter_list[i]['driver_profile'])
                                                                 
                self.vehicle_agent_list.append(vehicleAgent)


                pass
        

        # for i in range(len(self.vehicle_list)):
        #     vehicleAgent = self.vehicleFactory.createCogModAgent(id=self.vehicle_list[i].id,
        #                                                          vehicle=self.vehicle_list[i],
        #                                                          destinationPoint=self.agent_parameter_list[i]['destination_point'],
        #                                                          driver_profile=self.agent_parameter_list[i]['driver_profile'])
                                                                 
        #     self.vehicle_agent_list.append(vehicleAgent)
        #     pass
        pass


   


    #region simulation
    def run(self, maxTicks=5000):
        print('inside run research')
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.createVehicleAsynchoronousMode()
            self.world.wait_for_tick()
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.createVehicleSynchoronousMode()
            self.world.tick()
        
        for agent in self.vehicle_agent_list:
            print(f'agent : {agent}')
            self.visualizer.trackAgentOnTick(agent)

        onTickers = [self.visualizer.onTick, self.onTick]
        # onTickers = [self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)

        # print(time.time)
        # time.sleep(2)
        # print(time.time)
        self.simulator.run(maxTicks)

        # try: 
        # except Exception as e:
        #     self.logger.exception(e)
        pass



    
    def onEnd(self):
        self.destoryActors()
    
    def destoryActors(self):
        for vehicle in self.vehicle_list:
            vehicle.destroy()
        self.vehicle_agent_list = []
        pass

    def onTick(self, world_snapshot):
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.updateVehiclesAsynchoronousMode(world_snapshot)
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.updateVehiclesSynchoronousMode(world_snapshot)

 
            
    def updateVehiclesSynchoronousMode(self, world_snapshot):
        batch = []
        if len(self.vehicle_list) == 0:
            self.logger.warn(f"No vehicle to update")
            exit()
            return

        agent_to_remove = []
        for agent in self.vehicle_agent_list:
            if agent.is_done():
                agent_to_remove.append(agent)
            else:
                control = agent.update_agent(self.vehicle_agent_list)
                if control is not None:
                    batch.append(carla.command.ApplyVehicleControl(agent.vehicle.id, control))


        for agent in agent_to_remove:
            destroy_command = carla.command.DestroyActor(agent.vehicle.id)
            batch.append(destroy_command)
            
        results = self.client.apply_batch_sync(batch, True)
        for i in range(len(results)):
            print(f'results : {results[i].actor_id}, {results[i].has_error()}')
        pass


    def updateVehiclesAsynchoronousMode(self, world_snapshot):
        if len(self.vehicle_list) == 0:
            self.logger.warn(f"No vehicle to update")
            exit()
            return

        agent_to_remove = []
        for agent in self.vehicle_agent_list:
            if agent.is_done():
                agent_to_remove.append(agent)
            else:
                control = agent.update_agent(self.vehicle_agent_list)
                if control is not None:
                    agent.vehicle.apply_control(control)

        for agent in agent_to_remove:
            self.vehicle_agent_list.remove(agent)
            self.vehicle_list.remove(agent.vehicle)
            agent.vehicle.destroy()
            
  
        pass
