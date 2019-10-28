import random
import numpy as np
from mesa import Agent

from crowd_evacuation import path_finding
from crowd_evacuation.exit_agent import ExitAgent
from crowd_evacuation.fire_agent import FireAgent
from crowd_evacuation.reasons import Reasons
from crowd_evacuation.wall_agent import WallAgent


class CivilianAgent(Agent):

    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self._known_exits = known_exits
        self._discarded_exits = set()
        self._willingness_to_follow_steward = random.uniform(0, 1)
        self._age = random.randrange(15, 65)
        self._weight = random.uniform(40, 100)
        self._goal = None
        self._interacted_with = []
        self._exit_point = (None, None)  # a tuple that stores the exit of the agent
        self._visual_range = self.calculate_visual_range(self._age)
        self._speed = self.calculate_speed(self._visual_range, self._weight)
        self._observed_fire = set()
        self._being_risky = random.randrange(0, 2)
        self._info_exchange = self.model.civil_info_exchange
        self.last_pos = None
        self.walks = []

    def calculate_visual_range(self, age):
        """
        :param age:
        :return: the visual range of the agent based on age
        """
        if age <= 45:
            visual_range = random.randrange(5, 7)  # randomness accounts for individual variation
        else:
            visual_range = random.randrange(4, 5)
        return visual_range

    def calculate_speed(self, visual_range, weight):
        """
        :param visual_range:
        :param weight:
        :return: speed according to age and size. Speed varies between 3 and 7 m/s as per previous studies
        """
        if weight > 70:
            speed = visual_range - random.randrange(1, 3)  # weight has negative penalty on the speed
        else:
            speed = 4  # else, the speed is the maximum speed which is set to 4
        return speed

    def print_attributes(self):
        print('-' * 20)
        print("Agent ", self.unique_id)
        print('-' * 20)
        print("Known exits: ", self._known_exits)
        print("Willingness to follow steward: ", self._willingness_to_follow_steward)
        print("Speed (m/s): ", self._speed)
        print("Age (years): ", self._age)
        print("Size (kg): ", self._weight)
        print("Closest exit: ", self._goal)
        print("Interacted with: ", self._interacted_with)
        print()
        print()

    def step(self):
        temp_last_pos = self.pos

        # First, an agent should look around for the surrounding agents & possible moving positions.
        surrounding_agents, possible_steps, contacting_objects = self._looking_around()

        for surrounding_agent in surrounding_agents:
            # As perceptual memory of Civil_agent, they will remember the location of observed fire.
            # Note, depending on the agent's level of being risky,
            # his walkable distance/range from fire during moving is decided.
            if isinstance(surrounding_agent, FireAgent):
                extended_fire_area = set(self.model.grid.get_neighborhood(surrounding_agent.pos, moore=True,
                                                                          include_center=True,
                                                                          radius=self._being_risky))
                self._observed_fire = self._observed_fire.union(extended_fire_area)
            # Also, if there is exit in agent's vision range, add it to known exits
            elif isinstance(surrounding_agent, ExitAgent):
                self._known_exits.append(surrounding_agent.pos)

            # Else if civilians should exchange information and there is any other civilian in the objects surrounding
            # the agent, communicate and exchange information.
            if self._info_exchange and isinstance(surrounding_agent, CivilianAgent):
                self._interact(surrounding_agent)

        self._determine_goal()
        if self._goal is None:
            self._move_random_dir(possible_steps, surrounding_agents)
        else:
            # Set as non_walkable the nodes in the graph that contain other people or fire hazards.
            non_walkable = set()
            for neighbour in contacting_objects:
                if isinstance(neighbour, CivilianAgent):
                    non_walkable.add(neighbour.pos)
            keys_set = set(self.model.graph.nodes.keys())  # double check that non walkable belong to the graph
            non_walkable = non_walkable.union(self._observed_fire).intersection(keys_set)
            # Calculates the shortest possible path to the agent's goal.
            best_path = path_finding.find_path(self.model.graph, self.pos, self._goal, non_walkable=non_walkable)
            if best_path is not None and self.model.grid.is_cell_empty(best_path[1]):
                self.decide_move_action(best_path)
            else:
                # If the exit is unreachable because of fire, discard that exit for future calculations. This reduces
                # workload for A* algorithm
                non_walkable = self._observed_fire.intersection(keys_set)
                path = path_finding.find_path(self.model.graph, self.pos, self._goal, non_walkable=non_walkable)
                if path is None:
                    self._discarded_exits.add(self._goal)
                self._move_random_dir(possible_steps, surrounding_agents)
        self.last_pos = temp_last_pos
        self.walks.append(self.pos)

    def decide_move_action(self, path):
        """
        :param path:
        :return: determines where the agents have to move and if the agent have been saved
        """
        if len(path) <= self._speed:
            upper_bound = len(path)
        else:
            # truncated the path according to the speed of the agent
            del (path[self._speed + 1:])
            upper_bound = self._speed + 1
        for i in range(1, upper_bound):
            # move the agent as long as the there are empty squares
            if self.model.grid.is_cell_empty(path[i]):
                self.model.grid.move_agent(self, path[i])
            # if the cell is not empty check if it is the goal
            elif path[i] == self._goal:
                self._exit_point = path[i]
                self.model.remove_agent(self, Reasons.SAVED)
            # else break the loop and wait next turn
            else:
                break

    def _move_random_dir(self, possible_steps, surrounding_agents):

        if possible_steps:
            # If agent can see any wall, they try to walking along the wall
            if any(isinstance(agent, WallAgent) for agent in surrounding_agents):
                # firstly, agent pick the closest wall agent among the all visible walls
                # and compute the distance from the wall
                surrounding_walls = list(filter(lambda a: isinstance(a, WallAgent), surrounding_agents))
                closest_wall = self._find_closest_agent(surrounding_walls)
                distance_from_wall = self._absolute_distance(self.pos, closest_wall.pos)

                # select cells that are just as close or closer to a wall than where we are standing right now
                next_possible_steps = []
                for step in possible_steps:
                    shortest_dis_to_wall, _ = self._calculate_distance_to_closest_agent(step, surrounding_walls)
                    # if the next possible step's distance between walls
                    if shortest_dis_to_wall <= distance_from_wall and step != self.last_pos:
                        next_possible_steps.append(step)

                # Now, pick one position to move :
                # If they saw fire before they try to move far away from the fire
                if self._observed_fire and next_possible_steps:
                    closest_fire = self._find_closest_point(self._observed_fire)
                    distance_from_fire = self._absolute_distance(self.pos, closest_fire)
                    for coords in next_possible_steps:
                        if distance_from_fire <= self._absolute_distance(coords, closest_fire):
                            self.model.grid.move_agent(self, coords)
                            break
                # if there is no fire around them OR agent didn't see the fire yet,
                # they just walk along wall in random direction
                else:
                    random_cell = random.choice(next_possible_steps if next_possible_steps else possible_steps)
                    self.model.grid.move_agent(self, random_cell)

            # If agent don't see any wall and see fire, run away opposite side of the closest fire
            elif any(isinstance(agent, FireAgent) for agent in surrounding_agents):
                closest_fire = self._find_closest_agent(filter(lambda a: isinstance(a, FireAgent), surrounding_agents))
                self._move_away_from_fire(closest_fire)
            # ELSE, they just walk randomly.
            else:
                self.model.grid.move_agent(self, random.choice(possible_steps))

    def _absolute_distance(self, x, y):
        """
        :param x:
        :param y:
        :return: the absolute distance between two objects
        """
        return abs(x[0] - y[0]) + abs(x[1] - y[1])

    def _determine_goal(self):
        """
        Determines the goal for the agent, so where he should be headed to. For now it is just the closest exit,
        but it could be a more complex function that includes human psychology (maybe you go towards a known exit,
        instead of a closer one..)

        Returns:
            (tuple): The coordinates where this agent is heading to.

        """
        exits = set(self._known_exits).difference(self._discarded_exits)
        distances = [self._absolute_distance(self.pos, x) for x in exits]
        if distances:
            self._goal = list(exits)[distances.index(min(distances))]
        else:
            self._goal = None

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
        """
        :param  agents
        :return: the closest agent to the agent
        """
        min_distance = 10000
        closest_agent = None
        for agent in agents:
            distance_to_agent = self._absolute_distance(self.pos, agent.pos)
            if distance_to_agent < min_distance:
                min_distance = distance_to_agent
                closest_agent = agent
        return closest_agent

    def _find_closest_point(self, points):
        """
        :param  points
        :return: the closest agent to the agent
        """
        min_distance = 10000
        closest_agent = None
        for point in points:
            distance_to_agent = self._absolute_distance(self.pos, point)
            if distance_to_agent < min_distance:
                min_distance = distance_to_agent
                closest_agent = point
        return closest_agent

    def _find_exit(self, surrounding_agents):
        """
        :param  surrounding agents
        :return: the closest exit to the agent in the surroundings
        """
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

    def _cannot_move(self, possible_steps):
        """
        :param possible_steps:
        :return: Returns True if there is no possible step the agent can make, otherwise returns False.
        """
        for x in possible_steps:
            if self.model.grid.is_cell_empty(x):
                return False
        return True

    # _interact: Interacts with neighboring agents to exchange information.
    def _interact(self, other):
        # if isinstance(other, CivilianAgent):  # Redundant
        # Exchange of information about known exits
        shared_known_exits = list(set(self._known_exits + other._known_exits))
        self._known_exits = shared_known_exits
        other._known_exits = shared_known_exits
        # Exchange of information about discarded exits
        shared_discarded_exits = self._discarded_exits.union(other._discarded_exits)
        self._discarded_exits = shared_discarded_exits
        other._discarded_exits = shared_discarded_exits
        # Exchange of information about known fire hazards
        shared_fire_hazards = self._observed_fire.union(other._observed_fire)
        self._observed_fire = shared_fire_hazards
        other._observed_fire = shared_fire_hazards

    def _looking_around(self):
        """
        :return: surrounding agents, possible moving positions and obstacles
        """
        # the list of objects surrounding an agent, 5x5 range, exclude the center where the agent is standing
        surrounding_agents = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False,
                                                           radius=self._visual_range)
        contacting_objects = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        possible_moving_range = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=1)
        # also checking where this poor agent can move to survive
        possible_steps = []
        for position in possible_moving_range:
            if self.model.grid.is_cell_empty(position):
                possible_steps.append(position)
        return surrounding_agents, possible_steps, contacting_objects

    def _move_away_from_fire(self, fire):
        # move towards the opposite direction of the fire
        my_x, my_y = self.pos
        opposite_direction = np.asarray([(my_x - fire.pos[0]), (my_y - fire.pos[1])])  # direction of escape
        # We normalize and find the unit vector of opposite_direction
        norm_dir = np.linalg.norm(opposite_direction)
        norm_dir = np.divide(opposite_direction, norm_dir)
        # And move 1 cell towards that direction TODO : now we are using different speed..
        new_pos = norm_dir + (my_x, my_y)
        new_pos = np.round(new_pos).astype(int)
        new_pos = (new_pos[0], new_pos[1])  # cast array to tuple
        # self.model.grid.get_neighbors(new_pos, moore=True, include_center=True, radius=0)
        if self.model.grid.is_cell_empty(new_pos):
            self.model.grid.move_agent(self, new_pos)

    def _calculate_distance_to_closest_agent(self, point, agents):
        distance_agent_pairs = [(self._absolute_distance(point, agent.pos), agent) for agent in agents]
        distance_agent_pairs = sorted(distance_agent_pairs, key=lambda p: p[0])
        return distance_agent_pairs[0]
        # Call it like this: distance, agent = self._calculate_distance_to_closest_agent(point, agents)

    def _compare_distances(self, closest_wall, possible_steps):
        distance_from_wall = self._absolute_distance(self.pos, closest_wall)
        distance_agent_pairs = [(self._absolute_distance(step, closest_wall), step) for step in possible_steps]
        distance_agent_pairs = sorted(distance_agent_pairs, key=lambda p: p[0])
        if distance_from_wall >= distance_agent_pairs[0]:
            return
