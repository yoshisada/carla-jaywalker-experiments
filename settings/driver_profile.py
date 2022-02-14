
driver_profile = {
    'driver1': {
        'server_settings': {
            'longterm_memory': {
                'queue_length': 10,
                'frequency': 5,
            },
            'complex_cognition': {
                'queue_length': 10,
                'frequency': 5,
            },
            'motor_control': {
                'queue_length': 10,
                'frequency': 5,
            },
        },
        'local_map': {
            'vehicle_tracking_radius': 100,
            'global_plan_sampling_resolution': 1.0,
        },
        'controller': {
            'lateral_PID': {
                'Kp': 1.0,
                'Ki': 0.0,
                'Kd': 0.0,
                'dt': 0.1,
            },
            'lateral_PID': {
                'Kp': 1.0,
                'Ki': 0.0,
                'Kd': 0.0,
                'dt': 0.1,
            },
            'max_throttle': 0.75,
            'max_brake': 0.3,
            'max_steering': 0.8,
            'offset': 0.0,
        },
        'subtasks_parameters': {
            'lane_keeping': {
                'desired_velocity': 3.5 , # m/s
                'safe_time_headway': 1.5, # s
                'max_acceleration': 0.73, # m/s^2
                'comfort_deceleration': 1.67, # m/s^2
                'acceleration_exponent': 4, 
                'minimum_distance': 2, # m
                'vehicle_length': 1, # m
            },
            'lane_following': {
                'far_distance': 15.0,
            },
        },
    }

}