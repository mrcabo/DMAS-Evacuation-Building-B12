from enum import Enum

from mesa import Agent
import random
import numpy as np


class Reasons(Enum):
    SAVED = 1
    KILLED_BY_FIRE = 2


class StewardAgent(Agent):
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self.__known_exits = known_exits


class WallAgent(Agent):
    """ A wall agent."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitAgent(Agent):
    """ An emergency exit agent."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class FireAgent(Agent):
    """ Fire Agent """

    def __init__(self, pos, model):
        """
        Create a new fire agent

        Args:
            pos: The tree's coordinates on the grid. Also it is the unique_id
            model: standard model reference for agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.condition = "On Fire"
        self.burned_delay = 5  # How many iter. steps will a fire agent wait until infecting neighboring squares
        self.delay_counter = 0

    def step(self):
        """
        Fire agents "On Fire" will spread after a certain delay.
        """
        if (self.condition == "On Fire") and (self.delay_counter >= self.burned_delay):
            fire_neighbors = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            for grid_space in fire_neighbors:
                # We store all the spaces within 1-block distance from the fire.
                # The fire will spread (create new agents) in the model class
                self.model.fire_spread_pos.append(grid_space)
            self.condition = "Burned Out"
        elif self.condition == "On Fire":
            self.delay_counter += 1

    def get_pos(self):
        return self.pos


class CivilianAgent(Agent):

    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self.__known_exits = known_exits  #  (x, y) pairs
        self.__strategy = "random"
        self.__willingness_to_follow_steward = random.uniform(0, 1)
        self.__speed = random.uniform(3, 10)
        self.__age = random.randrange(15, 65)
        self.__gender = random.choice(["M", "F"])
        self.__size = random.uniform(40, 100)
        self.__closest_exit = None

    def print_attributes(self):
        print('-' * 20)
        print("Agent ", self.unique_id)
        print('-' * 20)
        print("Known exits: ", self.__known_exits)
        print("Strategy: ", self.__strategy)
        print("Willingness to follow steward: ", self.__willingness_to_follow_steward)
        print("Speed (m/s): ", self.__speed)
        print("Age (years): ", self.__age)
        print("Gender: ", self.__gender)
        print("Size (kg): ", self.__size)
        print("Closest_exit: ", self.__closest_exit)
        print()
        print()

    def step(self):
        # self.print_attributes()

        # First, an agent should look around for the surrounding agents & possible moving positions
        surrounding_agents, possible_steps, contacting_objects = self.__looking_around()

        # Check this agent can survive or not..
        if any(isinstance(x, FireAgent) for x in contacting_objects) and self.__cannot_move(possible_steps):
            self.model.remove_agent(self, Reasons.KILLED_BY_FIRE)
            return

        # If this agent can move, then if there is fire next to this agent, should run away
        if isinstance(surrounding_agents, FireAgent):
            self.__fire_get_the_heck_outta_here(self, FireAgent)

        if self.__closest_exit is None:
            self.__determine_closest_exit()

        self.__take_shortest_path()

        # If the agent reaches the exit, remove the agent from the schedule and the grid.
        if self.__reached_exit():
            self.model.remove_agent(self, Reasons.SAVED)


    def __absolute_distance(self, x, y):
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    # __determine_closest_exit: Determines the closest known exit, based on the absolute distance.
    def __determine_closest_exit(self):
        distances = [self.__absolute_distance(self.pos, x) for x in self.__known_exits]
        self.__closest_exit = self.__known_exits[distances.index(min(distances))]

    # __take_shortest_path: Takes the shortest path to the closest exit.
    def __take_shortest_path(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        distances = [self.__absolute_distance(self.__closest_exit, x) for x in possible_steps]

        # Find the closest available position to the closest exit around the agent and move the agent there.
        while distances:
            new_position = possible_steps[distances.index(min(distances))]
            if self.model.grid.is_cell_empty(new_position):
                self.model.grid.move_agent(self, new_position)
                break
            del possible_steps[distances.index(min(distances))]
            del distances[distances.index(min(distances))]

    # __take_random_path: Takes a random path, ignoring the exit.
    def __take_random_path(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)

        # Find the closest available random position around the agent and move the agent there.
        while possible_steps:
            new_position = self.random.choice(possible_steps)
            if self.model.grid.is_cell_empty(new_position):
                self.model.grid.move_agent(self, new_position)
                break
            del possible_steps[possible_steps.index(new_position)]

    def __reached_exit(self):
        return self.pos == self.__closest_exit

    # __cannot_move: Returns True if there is no possible step the agent can make, otherwise it
    # returns False.
    def __cannot_move(self, possible_steps):
        for x in possible_steps:
            if self.model.grid.is_cell_empty(x):
                return False
        return True

    # __looking_around: an agents look around in visible range(5X5) and find out other agents.
    def __looking_around(self):
        # the list of objects surrounding an agent, 5x5 range, exclude the center where the agent is standing
        surrounding_agents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=2)
        contacting_objects = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        possible_moving_range = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=1)

        # also checking where this poor agent can move to survive
        possible_moving_position = []
        for position in possible_moving_range:
            if self.model.grid.is_cell_empty(position):
                possible_moving_position.append(position)

        return surrounding_agents, possible_moving_position, contacting_objects

    def __egress_movement(self, possible_moving_range):
        # an agent can move one grid at a tick / time step
        # -> it means 3 x 3 range should be checked to find empty place to move

        return

    def __fire_get_the_heck_outta_here(self, fire):
        # move towards the opposite direction of the fire
        my_x, my_y = self.pos
        opposite_direction = np.asarray([(my_x - fire.pos[0]), (my_y - fire.pos[1])])  # direction of escape
        # We normalize and find the unit vector of opposite_direction
        norm_dir = np.linalg.norm(opposite_direction)
        norm_dir = np.divide(opposite_direction, norm_dir)
        # And move 1 cell towards that direction
        new_pos = norm_dir + (my_x, my_y)
        new_pos = np.round(new_pos).astype(int)
        self.model.grid.move_agent(self, new_pos)
        # TODO: It's not checking if the position is empty before moving agent,
        #  program crashes. Also, if agent is sourrounded by multiple FireAgents,
        #  this func will be called multiple times in a row. I think the whole array
        #  of neighbors should be passed as argument and here pick only ONE fire
        #  agent from where to escape.
        #if self.model.grid.is_cell_empty(new_pos.tolist()):
        #    self.model.grid.move_agent(self, new_pos.tolist())
