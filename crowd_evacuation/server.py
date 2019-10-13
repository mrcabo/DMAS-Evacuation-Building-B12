from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel
from mesa.visualization.modules import CanvasGrid,TextElement, ChartModule, PieChartModule
from mesa.visualization.UserParam import UserSettableParameter

from crowd_evacuation.exit_agent import ExitAgent
from crowd_evacuation.wall_agent import WallAgent
from crowd_evacuation.fire_agent import FireAgent
from crowd_evacuation.civilian_agent import CivilianAgent
from crowd_evacuation.steward_agent import StewardAgent
from crowd_evacuation.model_legend import ModelLegend
from crowd_evacuation.introduction_text import IntroductionText

COLORS_FIRE = {"On Fire": "#880000",
               "Burned Out": "#000000"}


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
        if agent._gender == 'M':
            portrayal["Color"] = "blue"
        else:
            portrayal["Color"] = "purple"
        portrayal["Filled"] = "true"
        portrayal["r"] = agent._size/100
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

    elif type(agent) is StewardAgent:
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "gold"
        portrayal["Filled"] = "true"
        portrayal["r"] = 1.3
        portrayal["Layer"] = 1

    return portrayal


line_chart = ChartModule([{"Label": "Agents alive", "Color": "gray"},
                          {"Label": "Agents killed", "Color": "red"},
                          {"Label": "Agents saved", "Color": "green"}])
pie_chart = PieChartModule([{"Label": "Agents alive", "Color": "gray"},
                            {"Label": "Agents killed", "Color": "red"},
                            {"Label": "Agents saved", "Color": "green"}])

introduction = IntroductionText()
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)
legend = ModelLegend()

model_params = {
    "N": UserSettableParameter('slider', "Number of civilian agents", 100, 1, 1000, 1,
                               description="Choose how many civilian agents to include in the model"),
    "K": UserSettableParameter('slider', "Number of steward agents", 0, 0, 30, 1,
                               description="Choose how many steward agents to include in the model"),
    "width": 50,
    "height": 50
}


server = ModularServer(EvacuationModel,
                       [introduction, grid, legend, line_chart, pie_chart],
                       "Evacuation model",
                       model_params)
server.port = 8521
