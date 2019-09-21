from mesa import Agent
import random


class StewardAgent(Agent):
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self.__known_exits = known_exits


class WallAgent(Agent):
    """ A wall agent."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitAgent(Agent):
    """ An emergency agent."""

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

        self.__known_exits = known_exits
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
        self.print_attributes()

        surround_objects = self.__looking_around()
        for neighbouring_object in surround_objects:
            if isinstance(neighbouring_object, FireAgent):
                self.__fire_get_the_heck_outta_here(neighbouring_object)

        if self.__closest_exit is None:
            self.__determine_closest_exit()

        self.__take_shortest_path()

        # If the agent reaches the exit, remove the agent from the schedule and the grid.
        if (self.__reached_exit()):
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

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

    # __looking_around: an agents look around in some range and find out other agents.
    def __looking_around(self):
        # the list of objects surrounding an agent
        surroundings = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False,
                                                     radius=2)  # 5x5 range, exclude the center where the agent is standing
        return surroundings

    def __fire_get_the_heck_outta_here(self, fire):
        # move towards the opposite direction of the fire
        my_x, my_y = self.pos
        opposite_direction = (my_x + (my_x - fire.pos[0]), my_y + (my_y - fire.pos[1]))


        # TODO: It's not checking if the position is empty before moving agent,
        #  program crashes. Also, if agent is sourrounded by multiple FireAgents,
        #  this func will be called multiple times in a row. I think the whole array
        #  of neighbors should be passed as argument and here pick only ONE fire
        #  agent from where to escape.
        self.model.grid.move_agent(self, opposite_direction)
