from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.agents import CivilianAgent, FireAgent, StewardAgent


class EvacuationModel(Model):
    """A model of the evacuation of a building
    """

    def __init__(self, N=10, width=50, height=50):
        self.num_agents = N
        self.pos_exits = []  # Position of every exit of the building
        self.fire_spread_pos = []
        self.grid = SingleGrid(height, width, False)  # TODO: simple Grid for now. Could be a ContinuousSpace ?
        self.schedule = RandomActivation(self)  # Every tick, agents move in a different random order
        self.datacollector = DataCollector(
            model_reporters={"N": "num_agents"},
            agent_reporters={"Position": "pos"}
        )

        # Create fire DEBUG
        fire_agent = FireAgent((0, 0), self)
        self.schedule.add(fire_agent)
        self.grid.place_agent(fire_agent, (0, 0))

        # Create agents
        for i in range(self.num_agents):
            a = CivilianAgent(i, self, [(10, 0), (10, 30), (20, 20), (15, 3), (5, 4)])
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

        for pos in self.fire_spread_pos:
            if self.grid.is_cell_empty(pos):  # TODO: For now, later it doesn't
                # matter if its empty, it could be a person so we would have to kill them.. :(
                new_fire = FireAgent(pos, self)
                self.schedule.add(new_fire)
                self.grid.place_agent(new_fire, pos)

        self.fire_spread_pos = []
        # collect data
        self.datacollector.collect(self)

        # Halt if no more agents in the building
        if self.count_agents(self) == 0:
            self.running = False

    @staticmethod
    def count_agents(model):
        """
        Helper method to count agents alive and still in the building.
        """
        count = 0
        for agent in model.schedule.agents:
            agent_type = type(agent)
            if (agent_type == CivilianAgent) or (agent_type == StewardAgent):
                count += 1
        return count
