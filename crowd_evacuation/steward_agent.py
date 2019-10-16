from crowd_evacuation.civilian_agent import CivilianAgent
from crowd_evacuation import path_finding
from crowd_evacuation.reasons import Reasons


class StewardAgent(CivilianAgent):
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model, known_exits)

    def step(self):
        # self.print_attributes()

        # First, an agent should look around for the surrounding agents & possible moving positions.
        surrounding_agents, possible_steps, contacting_objects = self._looking_around()

        # TODO: This piece is making the path finding func to crash. Needs diagnosing
        # If there is any fire in the objects surrounding the agent, move the agent away from the fire.
        # if any(isinstance(x, FireAgent) for x in surrounding_agents):
        #     closest_fire = self._find_closest_agent(filter(lambda a: isinstance(a, FireAgent), surrounding_agents))
        #     self._move_away_from_fire(closest_fire)
        #     return

        # TODO: should we return or not? Should the steward keep moving? What if there are many people around it vs few?
        # The stewards should shout information to people around them. We can simulate this by making them interact
        # with every civilian in their surroundings.
        if any(isinstance(x, CivilianAgent) and not isinstance(x, StewardAgent) for x in surrounding_agents):
            for x in surrounding_agents:
                if isinstance(x, CivilianAgent):
                    self._interact(x)
                    self._interacted_with.append(x.unique_id)
            return


        # If there is no immediate danger for the agent, move the agent towards the closest exit. Remove
        # the agent from the schedule and the grid if the agent has exited the building.
        if self._goal is None:
            self._determine_closest_exit()
        path = path_finding.find_path(self.model.graph, self.pos, self._goal)
        # self._take_shortest_path(possible_steps)
        if path is not None:
            if self.model.grid.is_cell_empty(path[1]):
                self.model.grid.move_agent(self, path[1])
        # TODO: Save the exit point to the self._exitpoint..
        if self._reached_exit():
            self.model.remove_agent(self, Reasons.SAVED)