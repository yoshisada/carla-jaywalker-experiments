from cmath import pi
from agents.navigation.global_route_planner import GlobalRoutePlanner
import carla
import argparse
import logging
import random
import time
import eventlet
from qnactr.CogModAgent import CogModAgent
eventlet.monkey_patch()

from lib import SimulationVisualization, MapNames, MapManager, Simulator
from lib.state import StateManager

from qnactr.CentralExecutor import CentralExecutor
from qnactr.helper import from_start_to_destination

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

map = mapManager.map

visualizer.drawSpawnPoints()
visualizer.drawSpectatorPoint()
# visualizer.drawAllWaypoints(life_time=0.0)


bpLib = world.get_blueprint_library()
vehicleBps = bpLib.filter('vehicle.ford.mustang')
blueprint = random.choice(vehicleBps)

planning_dict = from_start_to_destination(map)

agents = []
number_spawned_agents = 2
for i in range(0, number_spawned_agents):
    spawnPoint, destination_list = planning_dict.popitem()
    cogmod_driver = CogModAgent(world, blueprint, spawnPoint, random.choice(destination_list))
    cogmod_driver.create_global_plan()
    wpList = []
    for wp, _ in cogmod_driver.get_global_route():
        wpList.append(wp)
    visualizer.drawWaypoints(wpList, life_time=100.0)
    print(f'wpList: {wpList}')
    agents.append(cogmod_driver)

# while True:
#     for agent in agents:
#         agent.update_agent()


