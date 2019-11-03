from crowd_evacuation.civilian_agent import CivilianAgent

# The stewards should shout information to people around them. We can simulate this by making them interact
# with every civilian in their surroundings. Since the civilians already interact with every other civilian in
# their surroundings, the stewards will do this also, but the difference is that they will share knowledge of
# all the exits and make the goal of the civilians around them optimal.
class StewardAgent(CivilianAgent):
    def __init__(self, unique_id, model, known_exits):
        super().__init__(unique_id, model, known_exits)

        # Stewards should exchange information, irrespective of whether civilians do it or not.
        self._info_exchange = True
