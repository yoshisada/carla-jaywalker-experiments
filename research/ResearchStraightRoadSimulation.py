
from datetime import date
from enum import Enum
import os
from pickle import FALSE
import time
from tkinter import END
from tracemalloc import start
import carla
import pandas as pd
from lib.MapManager import MapNames
from lib.Simulator import Simulator
from agents.tools.misc import get_speed
from lib.SimulationMode import SimulationMode
from research.BaseResearch import BaseResearch

from settings.straight_road_settings import scenario_settings
from settings import SettingsManager

from agents.vehicles import VehicleFactory

# base research class for controlloing the whole simulation

class ScenarioState(Enum):
    START = 0
    RUNNING = 1
    END = 2
    PENDING = 3
    DISCARD = 4
    pass


class ResearchStraightRoadSimulation(BaseResearch):
    def __init__(self, client: carla.Client, 
                 mapName,
                 logLevel, 
                 outputDir:str = "logs", 
                 simulationMode = SimulationMode.ASYNCHRONOUS,
                 simulation_id = "setting1",
                 maxEpisode = 10):

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
        
        self.scenario_state = ScenarioState.PENDING
        self.episode_count = 0
        self.statDataframe = pd.DataFrame()
        self.max_episodes = maxEpisode
        self.setup()
        pass


    def setup(self):
        self.settingsManager.load(self.simulation_id)
        self.cogmod_agent_setting, self.actor_agent_setting, self.trigger_distance = self.settingsManager.getStraightRoadSimulationSettings()
        self.logger.info(f'setup with trigger distance {self.trigger_distance}')
        self.initStatDict()
        pass

    def destoryActors(self):
        if self.cogmod_agent is not None:
            self.logger.warn(f'destroying cogmod agent ')
            self.cogmod_agent.get_vehicle().destroy()
            self.cogmod_agent = None
        if self.actor_agent is not None:
            self.logger.warn(f'destroying actor agent ')
            self.actor_agent.get_vehicle().destroy()
            self.actor_agent = None
        pass

    def onEnd(self):
        self.logger.info("onEnd")
        self.destoryActors()
        self.global_agent_list = []
        pass

    def onTick(self, world_snapshot):
        self.updateVehiclesAsynchoronousMode()
        pass

    def updateVehiclesAsynchoronousMode(self):
        # print(f'update vehicle, cogmod agent {self.cogmod_agent.is_done()}')
        # print(f'update vehicle, actor agent {self.actor_agent.done()}')
        if self.cogmod_agent is None or self.actor_agent is None:
            self.logger.error("one or both the agent is None, ending simulation")
            return
        if self.cogmod_agent.is_done() or self.actor_agent.done():
            self.scenario_state = ScenarioState.END
            self.logger.info("one or both the agent is done destory actors")
            return
        
        cogmod_control = self.cogmod_agent.update_agent(self.global_agent_list)
        if cogmod_control is not None:
            self.cogmod_agent.vehicle.apply_control(cogmod_control)
        # print(f'vehicle at front {self.cogmod_agent.local_map.vehicle_at_front}')


        actor_location = self.actor_agent.get_vehicle().get_location()
        cogmod_location = self.cogmod_agent.get_vehicle().get_location()

        distance = actor_location.distance(cogmod_location)

        actor_control = carla.VehicleControl()
        if distance < self.trigger_distance and self.scenario_state == ScenarioState.START:
            actor_control = self.actor_agent.add_emergency_stop(actor_control)
            self.scenario_state = ScenarioState.RUNNING
            # self.start_scenario = True
        elif self.scenario_state == ScenarioState.PENDING:
            actor_control = self.actor_agent.run_step()
        if actor_control is not None:
            self.actor_agent._vehicle.apply_control(actor_control)

        pass

    def initStatDict(self):
        self.statDict = {
            "episode": [],
            "frame": [],
            "scenario_state": [],

            "c_x": [],
            "c_y": [],
            "c_speed": [],
            "c_steer": [],
            "c_throttle": [],
            "c_brake": [],
            # "v_direction": [],
            "a_x": [],
            "a_y": [],
            "a_speed": [],
            "a_steer": [],
            "a_throttle": [],
            "a_brake": [],
            # "w_direction": []
        }

        pass
    
    def collectStats(self, world_snapshot):

        self.statDict["episode"].append(self.episode_count)
        self.statDict["frame"].append(world_snapshot.frame)
        self.statDict["scenario_state"].append(self.scenario_state)

        self.statDict["c_x"].append(self.cogmod_agent.get_vehicle().get_location().x)
        self.statDict["c_y"].append(self.cogmod_agent.get_vehicle().get_location().y)
        self.statDict["c_speed"].append(self.cogmod_agent.get_vehicle().get_velocity().length())
        self.statDict["c_steer"].append(self.cogmod_agent.get_vehicle().get_control().steer)
        self.statDict["c_throttle"].append(self.cogmod_agent.get_vehicle().get_control().throttle)
        self.statDict["c_brake"].append(self.cogmod_agent.get_vehicle().get_control().brake)

        self.statDict["a_x"].append(self.actor_agent.get_vehicle().get_location().x)
        self.statDict["a_y"].append(self.actor_agent.get_vehicle().get_location().y)
        self.statDict["a_speed"].append(self.actor_agent.get_vehicle().get_velocity().length())
        self.statDict["a_steer"].append(self.actor_agent.get_vehicle().get_control().steer)
        self.statDict["a_throttle"].append(self.actor_agent.get_vehicle().get_control().throttle)
        self.statDict["a_brake"].append(self.actor_agent.get_vehicle().get_control().brake)

        # print('printing statdict')
        # print(self.statDict)
        pass

    def updateStatDataframe(self):
        # 1. make a dataframe from self.statDict
        df = pd.DataFrame.from_dict(self.statDict)
        # 2. merge it with the statDataframe
        print(f'before merge {self.statDataframe.shape}')
        self.statDataframe = pd.concat([self.statDataframe, df], ignore_index=True)
        print(f'after merge {self.statDataframe.shape}')
        # 3. clear self.statDict
        self.initStatDict()


    def run(self, maxTicks=5000):
        self.logger.info(f'start simulation maxTicks {maxTicks}')
        self.episode_count = 1

        if self.simulationMode == SimulationMode.ASYNCHRONOUS:
            self.createCogmodAgentsAsynchronousMode()
            self.createActorAgentsAsynchronousMode()
            self.world.wait_for_tick()
        # if self.simulationMode == SimulationMode.SYNCHRONOUS:
        #     self.logger.warn("synchronous mode is not implemented yet")
        #     pass
        
        time.sleep(2.0)

        onTickers = [self.onTick, self.collectStats, self.checkScenarioState]
        # onTickers = [self.onTick]
        onEnders = [self.onEnd]

        self.simulator = Simulator(self.client, onTickers=onTickers, onEnders=onEnders, simulationMode=self.simulationMode)
        self.simulator.run(maxTicks)
        pass

    def saveStats(self):
        dateStr = date.today().strftime("%m-%d-%Y")
        statsPath = os.path.join(self.outputDir, f"{dateStr}-trajectories.csv")
        # df = pd.DataFrame.from_dict(self.statDict)
        # df.to_csv(statsPath, index=False)

        if len(self.statDataframe) == 0:
            self.logger.warn("Empty stats. It means no episode was completed in this run")
            return
        self.statDataframe.to_csv(statsPath, index=False)
        pass

    def restartEpisode(self):
        self.episode_count += 1
        self.updateStatDataframe()
        self.logger.info(f'restarting scenario {self.episode_count}')
        if self.episode_count == self.max_episodes:
            self.saveStats()
            self.logger.info(f'episode {self.episode_count} completed, saving stats')
            exit()
            pass
        self.scenario_state = ScenarioState.PENDING
        self.createCogmodAgentsAsynchronousMode()
        self.createActorAgentsAsynchronousMode()
        self.world.wait_for_tick()
        time.sleep(2.0)
        pass

    def checkScenarioState(self, world_snapshot):

        actor_speed_threshold = 8
        cogmod_speed_threshold = 15
        start_distance_threshold = 1

        updated_distance_threshold = self.trigger_distance + start_distance_threshold

        actor_location = self.actor_agent.get_vehicle().get_location()
        cogmod_location = self.cogmod_agent.get_vehicle().get_location()

        actor_speed = get_speed(self.actor_agent.get_vehicle())
        cogmod_speed = get_speed(self.cogmod_agent.get_vehicle())

        if self.scenario_state == ScenarioState.DISCARD or self.scenario_state == ScenarioState.END:
            self.onEnd()
            self.restartEpisode()
            return
        
        if self.scenario_state == ScenarioState.PENDING:
            distance = actor_location.distance(cogmod_location)
            if distance < updated_distance_threshold and actor_speed >= actor_speed_threshold and cogmod_speed >= cogmod_speed_threshold: 
                self.scenario_state = ScenarioState.START
                self.logger.info(f'start scenario')
            elif distance < updated_distance_threshold and (actor_speed < actor_speed_threshold or cogmod_speed < cogmod_speed_threshold):
                self.logger.info(f'discarding scenario')
                self.scenario_state = ScenarioState.DISCARD
                pass
        elif self.scenario_state == ScenarioState.RUNNING:
            rounded_actor_speed = int(actor_speed)
            rounded_cogmod_speed = int(cogmod_speed)
            
            if rounded_actor_speed == 0 and rounded_cogmod_speed == 0:
                self.scenario_state = ScenarioState.END
                self.logger.info(f'end scenario')
            pass
        
        
        
        pass

    def createCogmodAgentsAsynchronousMode(self):
        spawn_transform = self.cogmod_agent_setting["spawn_transform"]
        destination_transform = self.cogmod_agent_setting["destination_transform"]
        driver_profile = self.cogmod_agent_setting["driver_profile"]

        vehicle = self.vehicleFactory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error("Could not spawn a vehicle")
            exit("cannot spawn cogmod vehicle")
        else:
            self.logger.info(f"successfully spawned cogmod actor {vehicle.id}")
            # self.logger.info(vehicle.get_control())

        self.cogmod_agent = self.vehicleFactory.createCogModAgent(1, vehicle, destination_transform, driver_profile)
        self.global_agent_list.append(self.cogmod_agent)
        pass

    def createActorAgentsAsynchronousMode(self):
        spawn_transform = self.actor_agent_setting["spawn_transform"]
        destination_transform = self.actor_agent_setting["destination_transform"]
        driver_profile = self.actor_agent_setting["driver_profile"]
        target_speed = self.actor_agent_setting["target_speed"]

        vehicle = self.vehicleFactory.spawn(spawn_transform)
        if vehicle is None:
            self.logger.error("Could not spawn actor vehicle")
            exit("cannot spawn actor vehicle")
        else:
            self.logger.info(f"successfully spawned actor vehicle {vehicle.id}")
            # self.logger.info(vehicle.get_control())

        self.actor_agent = self.vehicleFactory.createAgent(vehicle=vehicle,
                                                           target_speed=target_speed)
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


    # def printStatOnTick(self, world_snapshot):
    #     actor_location = self.actor_agent.get_vehicle().get_location()
    #     cogmod_location = self.cogmod_agent.get_vehicle().get_location()

    #     # actor_speed = self.actor_agent.get_vehicle().get_velocity()
    #     actor_speed = get_speed(self.actor_agent.get_vehicle())
    #     cogmod_speed = get_speed(self.cogmod_agent.get_vehicle())

    #     cogmod_control = self.cogmod_agent.get_vehicle().get_control()
    #     actor_control = self.actor_agent.get_vehicle().get_control()

    #     distance = actor_location.distance(cogmod_location)
        
    #     self.logger.info(f'{world_snapshot}, {self.scenario_state}, ego speed {round(cogmod_speed,2)}, control {cogmod_control}, actor speed {round(actor_speed,2)}, control {actor_control}, distance {round(distance, 2)}')
        
        # print(f'ego target vel from motor server {self.cogmod_agent.motor_control.target_velocity}')
        # pass


    