import random

import numpy as np

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.agents import CivilianAgent, FireAgent, StewardAgent, WallAgent, ExitAgent, Reasons
import random
from random import randint


class EvacuationModel(Model):
    """A model of the evacuation of a building
    """

    def __init__(self, N=10, width=50, height=50):
        self.num_agents = N
        self.pos_exits = []  # Position of every exit of the building
        # self.num_exits = 4 # number of exits : due to agents' pre-knowledge of exits
        self.fire_spread_pos = []
        self.agents_alive = N  # Agents alive and inside the building
        # TODO: maybe have an agents_saved array so we know through which exits these agents were saved?
        self.agents_saved = 0  # Agents that managed to get out
        self.agents_killed = 0  # Agents that perished during the evacuation
        self.grid = SingleGrid(height, width, False)
        self.schedule = RandomActivation(self)  # Every tick, agents move in a different random order
        self.datacollector = DataCollector(
            model_reporters={"Agents alive": "agents_alive",
                             "Agents killed": "agents_killed",
                             "Agents saved": "agents_saved"}
        )

        # TODO: exits should be defined only once here, and passed to draw environment to place "agents
        # Create exits
        exits = []
        # num_exits = 4
        for i in range(20, 25):  # draw emergency exits
            exits.append((i, 2))
        for i in range(20, 25):  # draw emergency exits
            exits.append((i, self.grid.height - 3))
        for i in range(10, 15):  # draw emergency exits
            exits.append((2, i))
        for i in range(30, 35):  # draw emergency exits
            exits.append((self.grid.width - 3, i))

        self.draw_environment()

        # Create fire DEBUG
        fire_initial_pos = [(11, 16)]
        for pos in fire_initial_pos:
            fire_agent = FireAgent(pos, self)
            self.schedule.add(fire_agent)
            self.grid.place_agent(fire_agent, pos)

        # Create agents
        middle_of_known_exits = exits[2::5]
        for i in range(self.num_agents):

            # an agent will know at least one exit from the pos_exits
            known_exits = random.sample(middle_of_known_exits, randint(1, len(middle_of_known_exits)))
            a = CivilianAgent(i, self, known_exits)

            self.schedule.add(a)
            # Add the agent to a random grid cell
            not_empty = True
            while not_empty:
                x = self.random.randrange(2, self.grid.width - 3)
                y = self.random.randrange(2, self.grid.height - 3)
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

    def remove_agent(self, agent, reason, **kwargs):
        """
        Removes an agent from the simulation. Depending on the reason it can be
        Args:
            agent (Agent):
            reason (Reasons):

        Returns:
            None
        """
        if reason == Reasons.SAVED:
            self.agents_saved += 1
        elif reason == Reasons.KILLED_BY_FIRE:
            self.agents_killed += 1

        self.agents_alive -= 1
        self.schedule.remove(agent)
        self.grid.remove_agent(agent)

    def draw_environment(self, exits=None):
        length_E = int(self.grid.height / 5)  # length of the vertical segments of the E
        depth_E = int(self.grid.width / 2)  # length of the horizontal segments of the E
        for i in range(3):
            start = max(0, 2 * i * length_E)
            self.draw_wall((0, start), (0, start + length_E - 1))
        for i in range(2):
            start = 2 * i * length_E + length_E
            self.draw_wall((depth_E, start), (depth_E, start + length_E - 1))
        # Horizontal lines of the E (BB)
        aux_y_coord = [length_E, 2 * length_E, 3 * length_E - 1, 4 * length_E - 1]
        for y in aux_y_coord:
            self.draw_wall((0, y), (depth_E, y))

        top_left_corner = (0, self.grid.height - 1)
        top_right_corner = (self.grid.width - 1, self.grid.height - 1)
        bottom_right_corner = (self.grid.width - 1, 0)
        self.draw_wall((0, 0), bottom_right_corner)
        self.draw_wall(top_left_corner, top_right_corner)
        self.draw_wall(bottom_right_corner, top_right_corner)

    def draw_wall(self, start, end):
        """
        Draws a line that goes from start point to end point.

        Args:
            start (List): Coordinates of line's starting point
            end (List): Coordinates of line's end point

        Returns:
            None
        """
        diff_x, diff_y = np.subtract(end, start)
        wall_coordinates = np.asarray(start)

        if self.grid.is_cell_empty(wall_coordinates.tolist()):
            w = WallAgent(wall_coordinates.tolist(), self)
            self.grid.place_agent(w, wall_coordinates.tolist())

        while diff_x != 0 or diff_y != 0:
            if abs(diff_x) == abs(diff_y):
                # diagonal wall
                wall_coordinates[0] += np.sign(diff_x)
                wall_coordinates[1] += np.sign(diff_y)
                diff_x -= 1
                diff_y -= 1
            elif abs(diff_x) < abs(diff_y):
                # wall built in y dimension
                wall_coordinates[1] += np.sign(diff_y)
                diff_y -= 1
            else:
                # wall built in x dimension
                wall_coordinates[0] += np.sign(diff_x)
                diff_x -= 1
            if self.grid.is_cell_empty(wall_coordinates.tolist()):
                w = WallAgent(wall_coordinates.tolist(), self)
                self.grid.place_agent(w, wall_coordinates.tolist())

    def draw_exits(self, exits_list):
        for ext in exits_list:
            e = ExitAgent(ext, self)
            if self.grid.is_cell_empty(ext):
                # Only walls should exist in the grid at this time, so no need to remove it from scheduler
                agent = self.grid.get_cell_list_contents(ext)
                self.grid.remove_agent(agent)
            # Place exit
            self.grid.place_agent(e, ext)

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
