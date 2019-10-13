from mesa import Agent

from crowd_evacuation.reasons import Reasons


class ExitAgent(Agent):
    """ An emergency exit agent."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        from crowd_evacuation.civilian_agent import CivilianAgent

        for agent in self.model.grid.get_neighbors(self.pos, moore=True, include_center=False):
            if isinstance(agent, CivilianAgent):
                self.model.remove_agent(agent, Reasons.SAVED)
