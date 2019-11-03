from functools import partial

import numpy as np

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector

from crowd_evacuation.exit_agent import ExitAgent
from crowd_evacuation.wall_agent import WallAgent
from crowd_evacuation.fire_agent import FireAgent
from crowd_evacuation.steward_agent import StewardAgent
from crowd_evacuation.civilian_agent import CivilianAgent
from crowd_evacuation.reasons import Reasons
from crowd_evacuation import path_finding


def count_agents_saved(exit_pos, model):
    exit_list = [agent._exit_point for agent in model.agents_saved]
    return exit_list.count(exit_pos)


class EvacuationModel(Model):
    """
    This is a simulation of a crowd evacuation from a building.
    Several variables are taken into account: the knowledge of the emergency exits, the age and weight of the agents
    and the presence of stewards that can guide agents toward the emergency exits.
    Agents have different strategies to escape the building such as taking the shortest path to an exit or a random one.

    The goal is to study which combinations of agent types are more likely to escape the building and save themselves and
    how the amount of casualties varies with respect to the different variables.
    """

    def __init__(self, N=10, K=0, width=50, height=50, fire_x=1, fire_y=1, civil_info_exchange=True):
        self.num_civilians = N
        self.num_stewards = K
        self.civil_info_exchange = civil_info_exchange
        self.fire_initial_pos = (fire_x, fire_y)
        self.warning_UI = ""
        self.agents_alive = N + K  # Agents alive and inside the building
        self.agents_saved = []  # Agents that managed to get out
        self.agents_killed = []  # Agents that perished during the evacuation
        self.grid = SingleGrid(height, width, False)
        self.graph = None  # General graph representing walkable terrain
        self.schedule = RandomActivation(self)  # Every tick, agents move in a different random order
        # Create exits
        self.pos_exits = [(0, 5), (0, 25), (0, 45)]
        for i in range(3):
            self.pos_exits.append((self.grid.width - 1, 14 + i))

        self.draw_environment(self.pos_exits)
        self.graph = path_finding.create_graph(self)
        # Define data collector
        model_collector = {"Agents killed": lambda killed: len(self.agents_killed),
                           "Agents saved": lambda saved: len(self.agents_saved)}
        for exit_pos in self.pos_exits:
            title = "Exit {}".format(exit_pos)
            model_collector[title] = partial(count_agents_saved, exit_pos)
        self.datacollector = DataCollector(
            model_reporters=model_collector
        )
        # Create fire
        # for pos in self.fire_initial_pos:  # Only 1 source of fire since we are setting it from UI
        x, y = self.fire_initial_pos
        if not self.is_inside_square((x, y), (0, 29), (25, 39)) and not self.is_inside_square(
                (x, y), (0, 10), (25, 20)):
            pos = self.fire_initial_pos
        else:
            pos = (1, 1)
            self.warning_UI = "<b>WARNING:</b> Sorry but the position of the fire is outside of the building, " \
                              "change the setting and click reset simulation."
        fire_agent = FireAgent(pos, self)
        self.schedule.add(fire_agent)
        self.grid.place_agent(fire_agent, pos)
        # Create civilian agents
        for i in range(self.num_civilians):

            # a civilian agent will know at least the main entrance to the building
            known_exits = self.pos_exits[-3:]
            a = CivilianAgent(i, self, known_exits)

            self.schedule.add(a)
            # Add the agent to a random grid cell

            while True:
                # pick the random coordinate
                x = self.random.randrange(1, self.grid.width - 1)
                y = self.random.randrange(1, self.grid.height - 1)
                # check if the point is empty and inside of the building
                if self.grid.is_cell_empty((x, y)) and not self.is_inside_square((x, y), (0, 29), (25, 39)) \
                        and not self.is_inside_square((x, y), (0, 10), (25, 20)):
                    break

            self.grid.place_agent(a, (x, y))

        # Create steward agents
        for i in range(self.num_civilians, self.num_civilians + self.num_stewards):

            # a steward agent will know all exits.
            known_exits = self.pos_exits
            a = StewardAgent(i, self, known_exits)

            self.schedule.add(a)
            # Add the agent to a random grid cell

            while True:
                # pick the random coordinate
                x = self.random.randrange(1, self.grid.width - 1)
                y = self.random.randrange(1, self.grid.height - 1)
                # check if the point is empty and inside of the building
                if self.grid.is_cell_empty((x, y)) and not self.is_inside_square((x, y), (0, 29), (25, 39)) \
                        and not self.is_inside_square((x, y), (0, 10), (25, 20)):
                    break

            self.grid.place_agent(a, (x, y))

        self.running = True  # Set this to false when we want to finish simulation (e.g. all agents are out of building)
        self.datacollector.collect(self)

    @staticmethod
    def is_inside_square(point, bottom_left, top_right):
        return bottom_left[0] <= point[0] <= top_right[0] and bottom_left[1] <= point[1] <= top_right[1]

    def step(self):
        self.schedule.step()
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
            self.agents_saved.append(agent)
        elif reason == Reasons.KILLED_BY_FIRE:
            self.agents_killed.append(agent)

        self.agents_alive -= 1
        # TODO: Add a saved agents list. We will save everything and then we analyze what we want.
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
        # Draw long contour lines E
        self.draw_wall((0, 0), bottom_right_corner)
        self.draw_wall(top_left_corner, top_right_corner)
        self.draw_wall(bottom_right_corner, top_right_corner)

        # Draw exits
        self.draw_exits(exits)

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
            if not self.grid.is_cell_empty(ext):
                # Only walls should exist in the grid at this time, so no need to remove it from scheduler
                agent = self.grid.get_cell_list_contents(ext)
                self.grid.remove_agent(agent[0])
            # Place exit
            self.schedule.add(e)
            self.grid.place_agent(e, ext)

    def spread_fire(self, fire_agent):
        fire_neighbors = self.grid.get_neighborhood(fire_agent.pos, moore=True, include_center=False)
        for grid_space in fire_neighbors:
            if self.grid.is_cell_empty(grid_space):
                # Create new fire agent and add it to grid and scheduler
                new_fire_agent = FireAgent(grid_space, self)
                self.schedule.add(new_fire_agent)
                self.grid.place_agent(new_fire_agent, grid_space)
            else:
                # If human agents, eliminate them and spread anyway
                agent = self.grid.get_cell_list_contents(grid_space)[0]
                if isinstance(agent, (CivilianAgent, StewardAgent)):
                    new_fire_agent = FireAgent(grid_space, self)
                    self.remove_agent(agent, Reasons.KILLED_BY_FIRE)
                    self.schedule.add(new_fire_agent)
                    self.grid.place_agent(new_fire_agent, grid_space)

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
