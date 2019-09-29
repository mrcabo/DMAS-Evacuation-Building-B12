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

        self._known_exits = known_exits


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

        self._known_exits = known_exits
        self._strategy = "random"
        self._willingness_to_follow_steward = random.uniform(0, 1)
        self._speed = random.uniform(3, 10)
        self._age = random.randrange(15, 65)
        self._gender = random.choice(["M", "F"])
        self._size = random.uniform(40, 100)
        self._closest_exit = None
        self._interacted_with = []

    def print_attributes(self):
        print('-' * 20)
        print("Agent ", self.unique_id)
        print('-' * 20)
        print("Known exits: ", self._known_exits)
        print("Strategy: ", self._strategy)
        print("Willingness to follow steward: ", self._willingness_to_follow_steward)
        print("Speed (m/s): ", self._speed)
        print("Age (years): ", self._age)
        print("Gender: ", self._gender)
        print("Size (kg): ", self._size)
        print("Closest exit: ", self._closest_exit)
        print("Interacted with: ", self._interacted_with)
        print()
        print()

    def step(self):
        #self.print_attributes()

        if self._closest_exit is None:
            self._determine_closest_exit()

        surround_objects = self._looking_around()
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        contacting_objects = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)

        # If there is a fire directly next to the agent and the agent cannot move, remove the agent
        # from the schedule and the grid.
        if any(isinstance(x, FireAgent) for x in contacting_objects) and self._cannot_move(possible_steps):
            self.model.remove_agent(self, Reasons.KILLED_BY_FIRE)
            return

        # Else if there is any fire in the objects surrounding the agent, move the agent away from the fire.
        for neighbouring_object in surround_objects:
            if isinstance(neighbouring_object, FireAgent):
                self._fire_get_the_heck_outta_here(neighbouring_object)
                return

        # Else if there is any other civilian in the objects surrounding the agent and they did not interact yet,
        # make them interact to exchange information.
        for neighbouring_object in surround_objects:
            if isinstance(neighbouring_object, CivilianAgent) and neighbouring_object.unique_id not in self._interacted_with:
              self._interact(neighbouring_object)
              self._interacted_with.append(neighbouring_object.unique_id)
              self._determine_closest_exit()
              return

        # Else if there is no immediate danger for the agent, move the agent towards the closest exit. Remove
        # the agent from the schedule and the grid if the agent has exited the building.
        self._take_shortest_path(possible_steps)
        if self._reached_exit():
            self.model.remove_agent(self, Reasons.SAVED)
  
    def _absolute_distance(self, x, y):
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    # _determine_closest_exit: Determines the closest known exit, based on the absolute distance.
    def _determine_closest_exit(self):
        distances = [self._absolute_distance(self.pos, x) for x in self._known_exits]
        self._closest_exit = self._known_exits[distances.index(min(distances))]

    # _take_shortest_path: Takes the shortest path to the closest exit.
    def _take_shortest_path(self, possible_steps):
        distances = [self._absolute_distance(self._closest_exit, x) for x in possible_steps]

        # Find the closest available position to the closest exit around the agent and move the agent there.
        while distances:
            new_position = possible_steps[distances.index(min(distances))]
            if self.model.grid.is_cell_empty(new_position):
                self.model.grid.move_agent(self, new_position)
                break
            del possible_steps[distances.index(min(distances))]
            del distances[distances.index(min(distances))]

    # _take_random_path: Takes a random path, ignoring the exit.
    def _take_random_path(self, possible_steps):
        # Find the closest available random position around the agent and move the agent there.
        while possible_steps:
            new_position = self.random.choice(possible_steps)
            if self.model.grid.is_cell_empty(new_position):
                self.model.grid.move_agent(self, new_position)
                break
            del possible_steps[possible_steps.index(new_position)]

    def _reached_exit(self):
        return self.pos == self._closest_exit

    # _cannot_move: Returns True if there is no possible step the agent can make, otherwise it
    # returns False.
    def _cannot_move(self, possible_steps):
        for x in possible_steps:
          if self.model.grid.is_cell_empty(x):
            return False
        return True

    # _interact: Interacts with neighboring agents to exchange information.
    def _interact(self, other):
      if isinstance(other, CivilianAgent):
        shared_known_exits = list(set(self._known_exits + other._known_exits))
        self._known_exits = shared_known_exits
        other._known_exits = shared_known_exits

    # _looking_around: an agents look around in some range and find out other agents.
    def _looking_around(self):
        # the list of objects surrounding an agent
        surroundings = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False,
                                                     radius=2)  # 5x5 range, exclude the center where the agent is standing
        return surroundings

    def _fire_get_the_heck_outta_here(self, fire):
        # move towards the opposite direction of the fire
        my_x, my_y = self.pos
        opposite_direction = np.asarray([(my_x - fire.pos[0]), (my_y - fire.pos[1])])  # direction of escape
        # We normalize the opposite_direction vector
        norm_dir = np.linalg.norm(opposite_direction)
        norm_dir = np.divide(opposite_direction, norm_dir)
        # And move 1 cell towards that direction
        new_pos = norm_dir + (my_x, my_y)
        new_pos = np.round(new_pos).astype(int)

        # TODO: It's not checking if the position is empty before moving agent,
        #  program crashes. Also, if agent is sourrounded by multiple FireAgents,
        #  this func will be called multiple times in a row. I think the whole array
        #  of neighbors should be passed as argument and here pick only ONE fire
        #  agent from where to escape.
        if self.model.grid.is_cell_empty(new_pos.tolist()):
            self.model.grid.move_agent(self, new_pos.tolist())
