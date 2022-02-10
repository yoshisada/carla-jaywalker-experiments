import click
from research import ResearchFactory

@click.command()
@click.option(        
    '--max_ticks',
    metavar='number',
    default=1000,
    type=int,
    help='Number of ticks the simulator will run'
    )
def ResearchCogMod(max_ticks):
    research = ResearchFactory.createResearchCogMod(maxTicks=max_ticks)


if __name__ == '__main__':
    ResearchCogMod()