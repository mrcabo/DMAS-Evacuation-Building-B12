from mesa import Agent
import random


class CivilianAgent(Agent):
    """ A civilian agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self._knowledge_of_exits = random.choice([False, True])
        self._position_of_entrance = None
        self._strategy = "random"
        self._willingness_to_follow_steward = random.uniform(0, 1)
        self._speed = random.uniform(3, 10)
        self._age = random.randrange(15, 65)
        self._gender = random.choice(["M", "F"])
        self._size = random.uniform(40, 100)

    def print_attributes(self):
      print('-' * 20)
      print("Agent ", self.unique_id)
      print('-' * 20)
      print("Knowledge of exits: ", self._knowledge_of_exits)
      print("Position of entrance: ", self._position_of_entrance)
      print("Strategy: ", self._strategy)
      print("Willingness to follow steward: ", self._willingness_to_follow_steward)
      print("Speed (m/s): ", self._speed)
      print("Age (years): ", self._age)
      print("Gender: ", self._gender)
      print("Size (kg): ", self._size)
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

