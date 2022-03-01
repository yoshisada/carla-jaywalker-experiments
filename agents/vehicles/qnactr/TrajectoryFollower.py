



class TrajectoryFollower():
    def __init__(self, vehicle, trajectory=None):
        super().__init__()
        self.name = "TrajectoryFollower"
        if trajectory is None or vehicle is None:
            return
        self.trajectory = trajectory
        self.vehicle = vehicle
        self.simulation_time = 0.0

    def update_agent(self):
        pass