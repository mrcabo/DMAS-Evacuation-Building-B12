from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel
from mesa.visualization.modules import CanvasGrid, TextElement, ChartModule, PieChartModule
from mesa.visualization.UserParam import UserSettableParameter

from crowd_evacuation.agents import CivilianAgent, FireAgent, WallAgent, ExitAgent

COLORS_FIRE = {"On Fire": "#880000",
               "Burned Out": "#000000"}


class IntroductionText(TextElement):
    """
    Display a text say hello .
    """

    def __init__(self):
        pass

    def render(self, model):
        text = '''<h1>Welcome to our evacuation
        simulation!</h1><p>Click Start to enjoy an entire simulation cycle,
        or click Step to calmly analyze what is happening. You can check out the
        code and report for this project
        <a href="https://github.com/mrcabo/DMAS-Evacuation-Building-B12">here</a>.</p>'''

        return text


def agent_portrayal(agent):
    """
    Determines how an agent will be drawn in the grid
    Args:
        agent (Agent): agent to be drawn

    Returns:
        Dictionary with the parameters required to draw agent
    """
    if agent is None:
        return

    portrayal = {}

    if type(agent) is CivilianAgent:
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "blue"
        portrayal["Filled"] = "true"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 1

    elif type(agent) is WallAgent:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "black"
        portrayal["Filled"] = "true"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["Layer"] = 0

    elif type(agent) is FireAgent:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = COLORS_FIRE[agent.condition]
        portrayal["Filled"] = "true"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Layer"] = 2

    elif type(agent) is ExitAgent:
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "green"
        portrayal["Filled"] = "true"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    return portrayal


line_chart = ChartModule([{"Label": "Agents alive", "Color": "gray"},
                          {"Label": "Agents killed", "Color": "red"},
                          {"Label": "Agents saved", "Color": "green"}])
pie_chart = PieChartModule([{"Label": "Agents alive", "Color": "gray"},
                            {"Label": "Agents killed", "Color": "red"},
                            {"Label": "Agents saved", "Color": "green"}])

introduction = IntroductionText()
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

model_params = {
    "N": UserSettableParameter('slider', "Number of agents", 400, 2, 2000, 1,
                               description="Choose how many agents to include in the model"),
    "width": 50,
    "height": 50
}

server = ModularServer(EvacuationModel,
                       [introduction, grid, line_chart, pie_chart],
                       "Evacuation model",
                       model_params)
server.port = 8521
