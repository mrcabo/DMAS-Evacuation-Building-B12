from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.agents import CivilianAgent, FireAgent, StewardAgent, WallAgent, ExitAgent


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

        self.draw_environment()

        # Create fire DEBUG
        fire_initial_pos = [(2, 2)]
        for pos in fire_initial_pos:
            fire_agent = FireAgent(pos, self)
            self.schedule.add(fire_agent)
            self.grid.place_agent(fire_agent, pos)

        # Create agents
        for i in range(self.num_agents):
            a = CivilianAgent(i, self, [(10, 0), (10, 30), (20, 20), (15, 3), (5, 4)])
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
