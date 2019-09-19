from mesa import Agent
import random


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

    def __reached_exit(self):
      return self.pos == self.__closest_exit
