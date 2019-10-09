from mesa import Agent


class ExitAgent(Agent):
    """ An emergency exit agent."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


