from .driver_profile import driver_profile
from .trajctory_follower_settings import trajectory_follower_settings

# In this scenario
# the vehicle is driving in a straigt road with one other vehicle at the front
# (1) speed of vehicle below (cogmod) is more than vehicle at front 
# (2) spawn distance between vehicles needs to be more than the trigger distance
# (3) both the vehicle accelerate to reach the target speed 
# (4) if the distance becomes less than the trigger distance before 
#     vehicle reaching target speed, we stop simulation
# (5) if both the vehicle reaches the target speed and the distance is more than the trigger distance,
#     we treat that as a valid simulation
# (6) if simulation is valid and the distance is less than the trigger distance 
#     vehicle at front brake and come to stop

scenario_settings = {
    "cogmod_agent": {
        "spawn_point": (-55, 8),
        "destination": (150, 8),
        "target_speed": 30.0,
        "driver_profile": driver_profile["DOM"],
    },
    'actor_agent': {
        "spawn_point": (3, 8),
        "destination_point": (150, 8),
        "target_speed": 20.0,
    },
    'trigger_distance': 20
} 