import math
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
        # self.pedFactory = PedestrianFactory(self.client, visualizer=self.visualizer)
        self.vehicleFactory = VehicleFactory(self.client, visualizer=self.visualizer)

        self.numberOfVehicles = 0
        self.vehicle_list = []
        self.vehicle_agent_list = []
        
        self.number_of_agents = 0
        self.agent_parameter_list = []
        
        self.setup()



    # def destoryActors(self):
    #     for vehicle in self.vehicle_list:
    #         vehicle.destroy()
    #     self.vehicle_agent_list = []
    #     pass

    def setup(self):
        self.settingsManager.load(self.simulation_id)
        self.simulator = None # populated when run
        self.number_of_agents, self.agent_parameter_list = self.settingsManager.getNumberOfAgentsWithParameters()
        pass




    def createVehicle(self):       

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

    def createVehicleCommand(self):       
        batch = []
        for i in range(self.number_of_agents):
            spawn_point = self.agent_parameter_list[i]['spawn_point']
            destination_point = self.agent_parameter_list[i]['destination_point']
            driver_profile = self.agent_parameter_list[i]['driver_profile']
           
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
                pass
        
        for vehicle in self.vehicle_list:
            vehicleAgent = self.vehicleFactory.createCogModAgent(id=vehicle.id,
                                                                 vehicle=vehicle,
                                                                 destinationPoint=destination_point,
                                                                 driver_profile=driver_profile)
                                                                 
            self.vehicle_agent_list.append(vehicleAgent)
            pass
        pass


   


    #region simulation
    def run(self, maxTicks=5000):
        print('inside run research')
        
        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.createVehicle()
            self.world.wait_for_tick()
        if self.simulationMode == SimulationMode.SYNCHRONOUS:
            self.createVehicleCommand()
            self.world.tick()

        

        onTickers = [self.visualizer.onTick, self.onTick]
        onTickers = [self.onTick]
        onEnders = [self.onEnd]
        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)

        self.simulator.run(maxTicks)

        # try: 
        # except Exception as e:
        #     self.logger.exception(e)
        pass



    
    def onEnd(self):
        self.destoryActors()

    def onTick(self, world_snapshot):
        self.updateVehicle(world_snapshot)
    
 
            
    def updateVehicle(self, world_snapshot):
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
  
        pass






##########################################################
#             Copied                                     #
##########################################################



    # def getWalkerSetting(self):
    #     walkerSettings = self.settingsManager.getWalkerSettings()
    #     walkerSetting = walkerSettings[1]
    #     return walkerSetting


    # def createWalker(self):
        
    #     # self.visualizer.drawWalkerNavigationPoints([self.walkerSpawnPoint])


    #     # self.walker = self.pedFactory.spawn(self.walkerSpawnPoint)

    #     # if self.walker is None:
    #     #     self.logger.error("Cannot spawn walker")
    #     #     exit("Cannot spawn walker")
    #     # else:
    #     #     self.logger.info(f"successfully spawn walker {self.walker.id} at {self.walkerSpawnPoint.location.x, self.walkerSpawnPoint.location.y, self.walkerSpawnPoint.location.z}")
    #     #     self.logger.info(self.walker.get_control())
            
    #     #     # visualizer.trackOnTick(walker.id, {"life_time": 1})      
        
    #     # self.world.wait_for_tick() # otherwise we can get wrong agent location!

    #     # self.walkerAgent = self.pedFactory.createAgent(walker=self.walker, logLevel=logging.DEBUG)

    #     # self.walkerAgent.setDestination(self.walkerDestination)
    #     # self.visualizer.drawDestinationPoint(self.walkerDestination)

    #     # attach actor manager

    #     pass




   
    # def updateWalker(self, world_snapshot):

    #     # print("updateWalker")

    #     if self.walkerAgent is None:
    #         self.logger.warn(f"No walker to update")
    #         return

    #     if self.walkerAgent.isFinished():
    #         print(f"Walker {self.walkerAgent.walker.id} reached destination. Going back")
    #         # if walkerAgent.destination == walkerSetting.destination:
    #         #     walkerAgent.set_destination(walkerSetting.source)
    #         #     visualizer.drawDestinationPoint(destination)
    #         # else:
    #         #     walkerAgent.set_destination(walkerSetting.destination)
    #         #     visualizer.drawDestinationPoint(destination)
    #         # return

    #     # print("canUpdate")
    #     # if self.walkerAgent.canUpdate():
    #     control = self.walkerAgent.calculateControl()
    #     # print("apply_control")
    #     self.walker.apply_control(control)





    # def restart(self, world_snapshot):
        
    #     if self.walkerAgent.isFinished():
    #         # 1. recreated vehicle
    #         self.recreateVehicle()
    #         # 2. reset walker
    #         self.resetWalker(reverse=False)

    
    # def recreateVehicle(self):
    #     # destroy current one
    #     # self.simulator.removeOnTicker()
    #     self.logger.warn(f"Recreating vehicle")
    #     self.vehicle.destroy()
    #     self.vehicleAgent = None
    #     self.vehicle = None
    #     self.createVehicle()

    # def resetWalker(self, reverse=False):

    #     # default keeps the same start and end as the first episode
    #     source = self.walkerSetting.source
    #     newDest = self.walkerSetting.destination

    #     if reverse:
    #         source =  self.walkerAgent.destination
    #         if self.walkerAgent.destination == newDest: # get back to source
    #             newDest = source
                

    #     self.walkerAgent.reset()
    #     self.walkerAgent.setDestination(self.walkerSetting.source)



    # def getNextDestination(self, currentLocation):

    #     return carla.Location(x=-132.862671, y=3, z=0.0)

    #     destination = random.choice(self.mapManager.spawn_points).location
    #     count = 1
    #     while destination.distance(currentLocation) < 5:
    #         destination = random.choice(self.mapManager.spawn_points).location
    #         count += 1
    #         if count > 5:
    #             self.logger.error(f"Cannot find a destination from {currentLocation}")
    #             raise Exception("Cannot find a destination")
    #     return destination



    ##########################################################
    #       Update agent                                #
    ##########################################################
          # temp = [-1, -1]
        # for i in range(len(self.vehicle_list)):
        #     steering_value = temp[i]
        #     # print(f'steering value================================================================: {steering_value}')
        #     control = carla.VehicleControl(throttle=0.1, steer=steering_value, brake=0.0, reverse=False, hand_brake=False, manual_gear_shift=False)
        #     self.vehicle_list[i].apply_control(control) 
        #     self.draw_steering_direction(self.vehicleAgent_list[i], 5.0)

        # # if self.vehicleAgent.done():
        # #     destination = random.choice(self.mapManager.spawn_points).location
        # #     # self.vehicleAgent.set_destination(destination, self.vehicle.get_location())
        # #     self.vehicleAgent.set_destination(destination)
        # #     self.logger.info("The target has been reached, searching for another target")
        # #     self.visualizer.drawDestinationPoint(destination)

        
        # control = self.vehicleAgent.run_step()
        # control.manual_gear_shift = False
        # self.logger.info(control)
        # self.vehicle.apply_control(control)









    




    ##########################################################
    #       DraW                                #
    ##########################################################


        # for i in range(self.numberOfVehicles):
        #     vehicleSpawnPoint = self.spawnPointTransforms[i]
        #     destinationPoint = self.destinationPointTransforms[i]
        #     vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)
        #     # self.world.wait_for_tick()
        #     if vehicle is None:
        #         self.logger.error("Cannot spawn vehicle")
        #         exit("Cannot spawn vehicle")
        #     else:
        #         self.logger.info(f"successfully spawn vehicle {vehicle.id} at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")   
            
        #     vehicleAgent = self.vehicleFactory.createCogModAgent(vehicle=vehicle, 
        #                                                          server_tick_frequency = server_tick_frequency[i], 
        #                                                          destinationPoint=destinationPoint)
            

            
        #     # vehicleAgent.set_destination(destinationPoint)

            


        #     self.visualizer.drawDestinationPoint(destinationPoint.location)
        #     print(f'drawing global plan for vehicle {vehicle.id}')
            
        #     # self.draw_global_plan(vehicleAgent)
            


        #     self.vehicle_list.append(vehicle)
        #     self.vehicle_agent_list.append(vehicleAgent)
        # # vehicleSpawnPoint = self.vehicleSpawnPoint
        # # # vehicleSpawnPoint = random.choice(self.mapManager.spawn_points)
        # # self.vehicle = self.vehicleFactory.spawn(vehicleSpawnPoint)       
        # # if self.vehicle is None:
        # #     self.logger.error("Cannot spawn vehicle")
        # #     exit("Cannot spawn vehicle")
        # # else:
        # #     self.logger.info(f"successfully spawn vehicle at {vehicleSpawnPoint.location.x, vehicleSpawnPoint.location.y, vehicleSpawnPoint.location.z}")

        # # self.world.wait_for_tick() # otherwise we can get wrong vehicle location!

        # # # self.vehicleAgent = self.vehicleFactory.createAgent(self.vehicle, target_speed=20, logLevel=logging.DEBUG)
        # # self.vehicleAgent = self.vehicleFactory.createBehaviorAgent(self.vehicle, behavior='normal', logLevel=logging.DEBUG)

        # # spawnXYLocation = carla.Location(x=vehicleSpawnPoint.location.x, y=vehicleSpawnPoint.location.y, z=0.001)
        # # destination = self.getNextDestination(spawnXYLocation)
        # # self.vehicleAgent.set_destination(destination, start_location=spawnXYLocation)
        



        
        
    # def draw_target_waypoint(self, agent):
    #     target_waypoint = agent.motor_control.target_waypoint
    #     if target_waypoint is not None:
    #         self.visualizer.drawWaypoints([target_waypoint], 
    #                                           color=(255, 0, 0), 
    #                                           z=1.5, 
    #                                           life_time=1)




    
    # def draw_global_plan(self, vehicleAgent):
    #     globalPlan = vehicleAgent.local_map.global_plan
    #     waypoints = []
    #     for wp, _ in globalPlan:
    #         waypoints.append(wp)
    #     self.visualizer.drawWaypoints(waypoints, color=(0, 255, 0), life_time=1)
    #     pass

    # def draw_steering_direction(self, vehicleAgent, line_size=5.0):
        
    #     vehicle_location = vehicleAgent._vehicle.get_location()
    #     vehicle_location = carla.Location(x=vehicle_location.x, y=vehicle_location.y, z=1.5)
    #     vehicle_forward_vector = vehicleAgent._vehicle.get_transform().get_forward_vector()

    #     control = vehicleAgent.get_vehicle_control()
    #     steering_angle = control.steer
        
        
    #     vehicle_forward_vector3D = carla.Vector3D(vehicle_forward_vector.x, vehicle_forward_vector.y, 0)
    #     vehicle_forward_vector_end_point = vehicle_location + carla.Vector3D(vehicle_forward_vector3D.x * line_size, vehicle_forward_vector3D.y * line_size, 0)

    #     steering_vector_x = vehicle_forward_vector3D.x * math.cos(steering_angle) - vehicle_forward_vector3D.y * math.sin(steering_angle)
    #     steering_vector_y = vehicle_forward_vector3D.x * math.sin(steering_angle) + vehicle_forward_vector3D.y * math.cos(steering_angle)

    #     steering_vector = carla.Vector3D(steering_vector_x*line_size, steering_vector_y*line_size, 1.5)
    #     steering_end_point = (steering_vector + vehicle_location)

    #     # print(f'vehicle_location : {vehicle_location}, end_point : {end_point}')

    #     vehicleAgent._world.debug.draw_line(vehicle_location, steering_end_point, life_time=1, color=carla.Color(0, 255, 0), thickness=0.2)
    #     vehicleAgent._world.debug.draw_line(vehicle_location, vehicle_forward_vector_end_point, life_time=0.5, color=carla.Color(255, 0, 0), thickness=0.2)
        

    #     pass
