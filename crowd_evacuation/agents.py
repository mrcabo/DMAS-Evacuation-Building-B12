from mesa import Agent
import random


class CivilianAgent(Agent):
    """ A civilian agent."""
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self.__known_exits = known_exits
        self.__strategy = "random"
        self.__willingness_to_follow_steward = random.uniform(0, 1)
        self.__speed = random.uniform(3, 10)
        self.__age = random.randrange(15, 65)
        self.__gender = random.choice(["M", "F"])
        self.__size = random.uniform(40, 100)

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
      print()
      print()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        if self.model.grid.is_cell_empty(new_position):
            self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()
        self.print_attributes()
        self.shortest_path()

    def __closest_exit():
      pass

    def __shortest_path(self):
      pass
    