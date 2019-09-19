from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.agents import CivilianAgent
from crowd_evacuation.agents import WallAgent
from crowd_evacuation.agents import ExitAgent

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

        self.draw_environment()
        # Create agents
        for i in range(self.num_agents):
            a = CivilianAgent(i, self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            not_empty = True
            while not_empty:
                x = self.random.randrange(2, self.grid.width-3)
                y = self.random.randrange(2, self.grid.height-3)
                if self.grid.is_cell_empty((x, y)):
                    not_empty = False
                    self.grid.place_agent(a, (x, y))

        self.running = True  # Set this to false when we want to finish simulation (e.g. all agents are out of building)
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def draw_environment(self):
        for i in range(2, self.grid.width-2):  # draw lower wall
            self.draw_wall(i, 1, i)

        for i in range(2, self.grid.width-2):  # draw upper wall
            self.draw_wall(i, self.grid.height-2, i)

        for i in range(1, 10):  # draw left wall
            self.draw_wall(1, i, i)

        for i in range(10, 15):    # draw emergency exits
            self.draw_exits(1, i, i)

        for i in range(15, self.grid.height-1):  # draw left wall
            self.draw_wall(1, i, i)

        for i in range(1, self.grid.height - 1):  # draw right wall
            self.draw_wall(self.grid.width-2, i, i)

    def draw_wall(self, x, y, i):
        w = WallAgent(i, self)
        not_empty = True
        while not_empty:
            if self.grid.is_cell_empty((x, y)):
                not_empty = False
                self.grid.place_agent(w, (x, y))

    def draw_exits(self, x, y, i):
        e = ExitAgent(i, self)
        not_empty = True
        while not_empty:
            if self.grid.is_cell_empty((x, y)):
                not_empty = False
                self.grid.place_agent(e, (x, y))


