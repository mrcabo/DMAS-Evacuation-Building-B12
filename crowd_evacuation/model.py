from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.agents import CivilianAgent


class EvacuationModel(Model):
    """A model of the evacuation of a building
    """
    def __init__(self, N=10, width=50, height=50):
        self.num_agents = N
        self.grid = SingleGrid(height, width, False)  # TODO: simple Grid for now. Could be a ContinuousSpace ?
        self.schedule = RandomActivation(self)  # Every tick, agents move in a different random order
        self.datacollector = DataCollector(
            model_reporters={"N": "num_agents"},
            agent_reporters={"Position": "pos"}
        )
        # Create agents
        for i in range(self.num_agents):
            a = CivilianAgent(i, self, [(10, 0), (10, 30)])
            self.schedule.add(a)
            # Add the agent to a random grid cell
            not_empty = True
            while not_empty:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                if self.grid.is_cell_empty((x, y)):
                    not_empty = False
                    self.grid.place_agent(a, (x, y))

        self.running = True  # Set this to false when we want to finish simulation (e.g. all agents are out of building)
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    # def run_model(self, n):
    #     for i in range(n):
    #         self.step()

