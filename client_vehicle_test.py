from cmath import pi
from agents.navigation.global_route_planner import GlobalRoutePlanner
import carla
import argparse
import logging
import random
import time
import eventlet
eventlet.monkey_patch()

from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error

from lib import SimulationVisualization, MapNames, MapManager, Simulator
from lib.state import StateManager

SpawnActor = carla.command.SpawnActor

argparser = argparse.ArgumentParser()

argparser.add_argument(
    '--host',
    metavar='H',
    default='127.0.0.1',
    help='IP of the host server (default: 127.0.0.1)')
argparser.add_argument(
    '-p', '--port',
    metavar='P',
    default=2000,
    type=int,
    help='TCP port to listen to (default: 3000)')
argparser.add_argument(
    '--tm-port',
    metavar='P',
    default=8000,
    type=int,
    help='Port to communicate with TM (default: 8000)')

args = argparser.parse_args()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

client = carla.Client(args.host, args.port)
client.set_timeout(5.0)

logging.info(f"Client carla version: {client.get_client_version()}")
logging.info(f"Server carla version: {client.get_server_version()}")

if client.get_client_version() != client.get_server_version():
    logging.warning("Client and server version mistmatch. May not work properly.")

SpawnActor = carla.command.SpawnActor

mapManager = MapManager(client)
mapManager.load(MapNames.t_junction)
# mapManager.load(MapNames.circle_t_junctions)

world = mapManager.world

visualizer = SimulationVisualization(client, mapManager)
# visualizer.draw00()

map = mapManager.map


visualizer.drawSpawnPoints()
visualizer.drawSpectatorPoint()
visualizer.drawAllWaypoints(life_time=0.0)



    
def from_start_to_destination():
    spawn_points = map.get_spawn_points()
    print(f'spawn points {len(spawn_points)}')
    global_route_planner = GlobalRoutePlanner(map, 2.0)
    
    start_end_dict = {}
    for start in range(0, len(spawn_points)):
        start_end_dict[spawn_points[start]] = []
        for end in range(0, len(spawn_points)):
            if start != end:
                start_location = spawn_points[start].location
                end_location = spawn_points[end].location
                try:
                    trace_route =  global_route_planner.trace_route(start_location, end_location)
                    # print(f'trace route {trace_route}')
                    temp_list = start_end_dict[spawn_points[start]]
                    temp_list.append(spawn_points[end].location)
                    start_end_dict[spawn_points[start]] = temp_list
                except:
                    pass
                pass
    planning_dict = {}
    for key in start_end_dict:
        if len(start_end_dict[key]) != 0:
            planning_dict[key] = start_end_dict[key]
        pass
    
    return planning_dict

planning_dict = from_start_to_destination()
print(f'planning dict {planning_dict}')

def spawn_vehicle(vehicleBP, spawnPoint, destination):
    if vehicleBP.has_attribute('color'):
        color = random.choice(vehicleBP.get_attribute('color').recommended_values)
        vehicleBP.set_attribute('color', color)
    if vehicleBP.has_attribute('driver_id'):
        driver_id = random.choice(vehicleBP.get_attribute('driver_id').recommended_values)
        vehicleBP.set_attribute('driver_id', driver_id)
    else:
        vehicleBP.set_attribute('role_name', 'autopilot')
    
    spawn_point_rotation = spawnPoint.rotation
    modified_rotation = carla.Rotation(spawn_point_rotation.pitch, spawn_point_rotation.yaw -180, spawn_point_rotation.roll)
    new_spawn_point = carla.Transform(spawnPoint.location, modified_rotation)
    vehicle = world.try_spawn_actor(vehicleBP, new_spawn_point)
    
    if vehicle is None:
        exit("Cannot spawn vehicle")
    else:
        print(f"successfully spawn vehicle at {spawnPoint.location.x, spawnPoint.location.y, spawnPoint.location.z}")
        print(vehicle.get_acceleration())
        print(vehicle.get_velocity())
        print(vehicle.get_location())
        print(vehicle.id)
        # vehicle.set_target_velocity(carla.Vector3D(10, 10))
        print(vehicle.get_velocity())    
    
    agent = BasicAgent(vehicle, target_speed=40)
    # destination = random.choice(mapManager.spawn_points).location
    agent.set_destination(destination)
    agent.ignore_stop_signs(active=False)
    visualizer.drawDestinationPoint(destination)
    
    return vehicle, agent
    
    pass

bpLib = world.get_blueprint_library()
vehicleBps = bpLib.filter('vehicle.ford.mustang')
blueprint = random.choice(vehicleBps)
# spawn_points = mapManager.spawn_points
# spawnPoint = random.choice(spawn_points)

vehicles, agents = [], []

spawnPoint, destination_list = planning_dict.popitem()
vehicle, agent = spawn_vehicle(blueprint, spawnPoint, random.choice(destination_list))
world.wait_for_tick()
vehicles.append(vehicle)
agents.append(agent) 

spawnPoint, destination_list = planning_dict.popitem()
spawnPoint, destination_list = planning_dict.popitem()

vehicle, agent = spawn_vehicle(blueprint, spawnPoint, random.choice(destination_list))
world.wait_for_tick()
vehicles.append(vehicle)
agents.append(agent) 

# spawnPoint, destination_list = planning_dict.popitem()
# vehicle, agent = spawn_vehicle(blueprint, spawnPoint, random.choice(destination_list))
# world.wait_for_tick()
# vehicles.append(vehicle)
# agents.append(agent) 

def destoryActor(vehicle, agent):
    print('\ndestroying  one vehicle')
    vehicles.remove(vehicle)
    agents.remove(agent)
    vehicle.destroy()

def destoryActors():
    print('\ndestroying  vehicles')
    for vehicle in vehicles:
        vehicles.remove(vehicle)
        vehicle.destroy()
    for agent in agents:
        agents.remove(agent)
    world.wait_for_tick()

def agentUpdate(world_snapshot):
    for i in range(0, len(vehicles)):
        agent = agents[i]
        if agent.done():
            # destination = random.choice(mapManager.spawn_points).location
            # agent.set_destination(destination)
            # print("The target has been reached, searching for another target")
            # visualizer.drawDestinationPoint(destination)
            destoryActor(vehicles[i], agent)

        control = agent.run_step()
        control.manual_gear_shift = False
        vehicles[i].apply_control(control)


stateManager = StateManager(client, trafficParticipants=vehicles)


onTickers = [visualizer.onTick, stateManager.onTick, agentUpdate]
onEnders = [destoryActors]
simulator = Simulator(client, onTickers=onTickers, onEnders=onEnders)

simulator.run(10000)



