from turtle import distance
import carla 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class GraphData():
    def __init__(self):
        self.frame = 0
        self.scenario_state = None

        self.ego_speed = -1
        self.ego_control = None
        # self.ego_location = None

        self.actor_speed = -1
        self.actor_control = None
        # self.actor_location = None

        self.distance = -1
        pass
    

class Analytics():
    def __init__(self, file_path, ):
        self.log_file_path = file_path
        self.discard_col = 10

        self.raw_data = self.read_log_file()
        self.scenario_overhead, self.main_scenario = self.clean_data()
        
        pass

    def read_log_file(self):
        with open(self.log_file_path) as f:
            lines = f.readlines()
            return lines
        
    def clean_data(self):
        scenario_overhead = []
        main_scenario = []
        is_main_scenario = False

        temp_data = self.raw_data[self.discard_col:]
        temp_data = [x.split(',') for x in temp_data]

        for data in temp_data:
            if len(data) == 2:
                if data[1].split("-")[3].split(" ")[1] == 'start':
                    # print(f'main scenario starting')
                    is_main_scenario = True
            elif len(data) == 20 and not is_main_scenario:
                # print(f'scenario overhead ')
                data_bucket = self.create_data_dict(data)
                scenario_overhead.append(data_bucket)
            elif len(data) == 20 and is_main_scenario:
                # print(f'main scenario')
                data_bucket = self.create_data_dict(data)
                main_scenario.append(data_bucket)

        return scenario_overhead, main_scenario

    def create_data_dict(self, data):
        data_bucket = GraphData()

        data_bucket.frame = int(data[1].split("=")[1].split(')')[0])
        data_bucket.scenario_state = data[2]

        data_bucket.ego_speed = float(data[3].split(" ")[3])
        ego_control = carla.VehicleControl()
        ego_control.throttle = float(data[4].split("(")[1].split("=")[1])
        ego_control.steer = float(data[5].split("=")[1])
        ego_control.brake = float(data[6].split("=")[1])
        data_bucket.ego_control = ego_control

        data_bucket.actor_speed = float(data[11].split(" ")[3])
        actor_control = carla.VehicleControl()
        actor_control.throttle = float(data[12].split("(")[1].split("=")[1])
        actor_control.steer = float(data[13].split("=")[1])
        actor_control.brake = float(data[14].split("=")[1])
        data_bucket.actor_control = actor_control

        data_bucket.distance = float(data[19].split(' ')[2])

        return data_bucket

            # print(len(data), data[19].split(' ')[2])

    def print_raw_data(self):
        print(f'length data {len(self.raw_data)}')
        for i in range(len(self.raw_data)):
            temp = self.raw_data[i]
            print(f'{i} : {temp}')

    def print_data_dict(self):
        self.print_scenario_overhead()
        self.print_main_scenario()
        pass

    def print_scenario_overhead(self):
        for data in self.scenario_overhead:
            print(data)
        pass

    def print_main_scenario(self):
        for data in self.main_scenario:
            print(data)
        pass

    def get_scenario_overhead(self):
        return self.scenario_overhead
    
    def get_main_scenario(self):
        return self.main_scenario

    
    def plot_full_scenario(self, x_axis, y_axis):
        xValue = []
        yValue = []

        for data in self.scenario_overhead:
            xValue.append(self.get_property_from_data(data, x_axis))
            yValue.append(self.get_property_from_data(data, y_axis))
            pass
        plt.plot(xValue, yValue, '-o')

        xValue = []
        yValue = []

        for data in self.main_scenario:
            xValue.append(self.get_property_from_data(data, x_axis))
            yValue.append(self.get_property_from_data(data, y_axis))
            pass
        plt.plot(xValue, yValue, '-x')
        plt.show()
        # for data in self.main_scenario:
        #     print(data)
        #     pass

    def get_property_from_data(self, data : GraphData, property):

        if property == 'frame':
            return data.frame
        elif property == 'scenario_state':
            return data.scenario_state
        elif property == 'ego_speed':
            return data.ego_speed
        elif property == 'ego_throttle':
            return data.ego_control.throttle
        elif property == 'ego_brake':
            return data.ego_control.brake
        elif property == 'ego_steering':
            return data.ego_control.steer
        elif property == 'actor_speed':
            return data.actor_speed
        elif property == 'actor_throttle':
            return data.actor_control.throttle
        elif property == 'actor_brake':
            return data.actor_control.brake
        elif property == 'actor_steering':
            return data.actor_control.steer
        elif property == 'distance':
            return data.distance
        pass



if __name__ == '__main__':
    log_file_path = '../logs/createStraightRoadSimulation.log'
    data_analytics = Analytics(log_file_path)

    data_analytics.plot_full_scenario(x_axis='frame', y_axis='ego_speed')
    
    

    
    # data_analytics.plot_raw_data()

    pass