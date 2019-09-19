from mesa import Agent


class CivilianAgent(Agent):
    """ A civilian agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        if self.model.grid.is_cell_empty(new_position):
            self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()


class WallAgent(Agent):
    """ A wall agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class ExitAgent(Agent):
    """ An emergency agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


