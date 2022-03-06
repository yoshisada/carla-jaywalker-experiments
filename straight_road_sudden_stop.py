import click
from research import ResearchFactory, SimulationMode

@click.command()
@click.option(
    '--max_ticks',
    metavar='number',
    default=2000,
    type=int,
    help='Number of ticks the simulator will run'
    )
def ResearchStraightRoadSuddenStop(max_ticks):
    research = ResearchFactory.createStraightRoadSimulation(maxTicks=max_ticks,
                                                            simulationMode=SimulationMode.ASYNCHRONOUS,
                                                            simulation_id = 'setting1')


if __name__ == '__main__':
    ResearchStraightRoadSuddenStop()
