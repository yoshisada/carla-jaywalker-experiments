

from agents.navigation.global_route_planner import GlobalRoutePlanner


def from_start_to_destination(map):

    # this function is used to get the possible start to destination dict
    # returns a dict of start to destination of the format:
            # { spawn_transform: [destination_transform1, destination_transform2, ...] }

    if map is None:
        raise ValueError('need to have map')
        return
    
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
                    temp_list.append(spawn_points[end])
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