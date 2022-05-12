import carla
import time

# connect to client

ghost = '127.0.0.1'

gport = 2000


client = carla.Client(ghost, gport)

#originally 10.0
client.set_timeout(20.0)

print("server ver: ", client.get_server_version)

print("client ver: ", client.get_client_version)

# get all available maps from client

print(client.get_available_maps())

# load world and get map

world = client.load_world('town02')

map = world.get_map()

bplib = world.get_blueprint_library()

pedestrian = bplib.filter('walker.pedestrian.0001')

pbp = pedestrian[0]

spawn_points = map.get_spawn_points()

count = 0
""""
for point in spawn_points:
    try:
        world.spawn_actor(pbp, point)
    except:
        print("collison")
"""

ped = world.spawn_actor(pbp, spawn_points[5])

world.get_spectator().set_transform(spawn_points[5])


time.sleep(30)

ped.destroy()