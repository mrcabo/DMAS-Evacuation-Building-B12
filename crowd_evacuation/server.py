from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel
from crowd_evacuation.agents import CivilianAgent
from crowd_evacuation.agents import WallAgent
from crowd_evacuation.agents import ExitAgent
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from crowd_evacuation.agents import CivilianAgent, FireAgent, WallAgent, ExitAgent

COLORS_FIRE = {"On Fire": "#880000",
               "Burned Out": "#000000"}


def agent_portrayal(agent):

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
        portrayal["Shape"] = "images/emergency.png"
        portrayal["Color"] = "green"
        portrayal["Filled"] = "true"
        portrayal["w"] = 0.8
        portrayal["h"] = 0.8
        portrayal["r"] = 0.8
        portrayal["Layer"] = 0

    return portrayal


grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

model_params = {
    "N": UserSettableParameter('slider', "Number of agents", 100, 2, 2000, 1,
                               description="Choose how many agents to include in the model"),
    "width": 50,
    "height": 50
}

server = ModularServer(EvacuationModel, [grid], "Evacuation model", model_params)
server.port = 8521
