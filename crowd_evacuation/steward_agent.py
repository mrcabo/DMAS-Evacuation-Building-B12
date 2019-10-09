from mesa import Agent


class StewardAgent(Agent):
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model)

        self._known_exits = known_exits
