from mesa import Agent
from crowd_evacuation.reasons import Reasons
import random
import numpy as np
from crowd_evacuation import path_finding
from crowd_evacuation.fire_agent import FireAgent
from crowd_evacuation.exit_agent import ExitAgent


class CivilianAgent(Agent):

    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self._known_exits = known_exits
        self._strategy = "random"
        self._willingness_to_follow_steward = random.uniform(0, 1)
        self._age = random.randrange(15, 65)
        self._gender = random.choice(["M", "F"])
        self._size = random.uniform(40, 100)
        self._goal = None
        self._interacted_with = []
        self._speed = self.calculate_speed(self._age, self._size)
        self.observed_fire = set()

    def calculate_speed(self, age, size):
        normal_speed = random.uniform(20, 30)
        speed = normal_speed - (age*0.1 + size*0.1)
        return round(speed, 1)

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
        print("Closest exit: ", self._goal)
        print("Interacted with: ", self._interacted_with)
        print()
        print()

    def step(self):
        self.print_attributes()

        # First, an agent should look around for the surrounding agents & possible moving positions.
        surrounding_agents, possible_steps, contacting_objects = self._looking_around()

        # As perceptional memory of Civil_agent, they will remember the location of observed fire
        for surrounding_agent in surrounding_agents:
            if isinstance(surrounding_agent, FireAgent):
                self.observed_fire.add(surrounding_agent.pos)
            elif isinstance(surrounding_agent, ExitAgent):
                self._goal = surrounding_agent.pos
        # If there is any fire in the objects surrounding the agent, move the agent away from the fire.
        # if any(isinstance(x, FireAgent) for x in surrounding_agents):
        #     closest_fire = self._find_closest_agent(filter(lambda a: isinstance(a, FireAgent), surrounding_agents))
        #     self._move_away_from_fire(closest_fire)
        #     return

        # Else if there is any other civilian in the objects surrounding the agent, find the closest civilian
        # that did not interact with the agent yet and make them interact to exchange information.
        if any(isinstance(x, CivilianAgent) for x in surrounding_agents):
            closest_new_civilian = self._find_closest_new_civilian(surrounding_agents)
            if closest_new_civilian is not None:
                self._interact(closest_new_civilian)
                self._interacted_with.append(closest_new_civilian.unique_id)
                self._determine_closest_exit()
                return

        # Else if there is no immediate danger for the agent, move the agent towards the closest exit. Remove
        # the agent from the schedule and the grid if the agent has exited the building.
        if self._goal is None:
            self._determine_closest_exit()

        non_walkable = []
        for neighbour in contacting_objects:
            if isinstance(neighbour, CivilianAgent):
                non_walkable.append(neighbour.pos)

        best_path = path_finding.find_path(self.model.graph, self.pos, self._goal, non_walkable=non_walkable)
        # self._take_shortest_path(possible_steps)
        if best_path is not None and self.model.grid.is_cell_empty(best_path[1]):
            self.model.grid.move_agent(self, best_path[1])
        else:
            # When agent doesn't have any known exit or their possible route is blocked by fire,
            # they will take one of possible_steps
            if possible_steps:
                self.model.grid.move_agent(self, random.choice(possible_steps))
        # TODO: ExitAgent will take out the people.
        # if any([isinstance(object, ExitAgent) for object in contacting_objects]):
        # if self._reached_exit():
        #     self.model.remove_agent(self, Reasons.SAVED)

    def _absolute_distance(self, x, y):
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    # _determine_closest_exit: Determines the closest known exit, based on the absolute distance.
    def _determine_closest_exit(self):
        distances = [self._absolute_distance(self.pos, x) for x in self._known_exits]
        self._goal = self._known_exits[distances.index(min(distances))]

    # _take_shortest_path: Takes the shortest path to the closest exit.
    def _take_shortest_path(self, possible_steps):
        distances = [self._absolute_distance(self._goal, x) for x in possible_steps]

        # Find the closest available position to the closest exit around the agent and move the agent there.
        while distances:
            new_position = possible_steps[distances.index(min(distances))]
            print(new_position)
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
        """
        Returns true when agent is in the Von Neumann neighborhood (exclude diagonals) of an exit

        Returns:
            (bool): if the agent has been saved or not
        """
        for exit_neighbour in self.model.grid.get_neighborhood(self._goal, moore=True):
            if self.pos == exit_neighbour:
                return True
        return False

    def _find_closest_agent(self, agents):
        min_distance = 10000
        closest_agent = None
        for agent in agents:
            distance_to_agent = self._absolute_distance(self.pos, agent.pos)
            if distance_to_agent < min_distance:
                min_distance = distance_to_agent
                closest_agent = agent
        return closest_agent

    def _find_exit(self, surrounding_agents):
        surrounding_exits = filter(lambda a: isinstance(a, ExitAgent), surrounding_agents)
        return self._find_closest_agent(surrounding_exits)

    def _find_closest_new_civilian(self, surrounding_agents):
        civilians = [x for x in surrounding_agents if isinstance(x, CivilianAgent)]
        while civilians:
            closest_civilian = self._find_closest_agent(civilians)
            if closest_civilian.unique_id not in self._interacted_with:
                return closest_civilian
            del civilians[civilians.index(closest_civilian)]
        return None

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

    # _looking_around: an agents look around in visible range(5X5) and find out other agents.
    def _looking_around(self):
        # the list of objects surrounding an agent, 5x5 range, exclude the center where the agent is standing
        surrounding_agents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False, radius=5)
        contacting_objects = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        possible_moving_range = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=1)

        # also checking where this poor agent can move to survive
        possible_moving_position = []
        for position in possible_moving_range:
            if self.model.grid.is_cell_empty(position):
                possible_moving_position.append(position)

        return surrounding_agents, possible_moving_position, contacting_objects

    def _egress_movement(self, possible_moving_range):
        # an agent can move one grid at a tick / time step
        # -> it means 3 x 3 range should be checked to find empty place to move

        return

    def _move_away_from_fire(self, fire):
        # move towards the opposite direction of the fire
        my_x, my_y = self.pos
        opposite_direction = np.asarray([(my_x - fire.pos[0]), (my_y - fire.pos[1])])  # direction of escape
        # We normalize and find the unit vector of opposite_direction
        norm_dir = np.linalg.norm(opposite_direction)
        norm_dir = np.divide(opposite_direction, norm_dir)
        # And move 1 cell towards that direction
        new_pos = norm_dir + (my_x, my_y)
        new_pos = np.round(new_pos).astype(int)
        # self.model.grid.move_agent(self, new_pos)
        # TODO: TBD - still not clear how to do it
        if self.model.grid.is_cell_empty(new_pos.tolist()):
            self.model.grid.move_agent(self, new_pos.tolist())
