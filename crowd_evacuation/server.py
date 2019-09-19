from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel
from crowd_evacuation.agents import CivilianAgent
from crowd_evacuation.agents import WallAgent
from crowd_evacuation.agents import ExitAgent
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


def agent_portrayal(agent):
    if type(agent) is WallAgent:
        portrayal = {"Shape": "rect",
                     "Color": "black",
                     "w": 0.8,
                     "h": 0.8,
                     "Filled": "true",
                     "Layer": 0}
    elif type(agent) is CivilianAgent:
        portrayal = {"Shape": "circle",
                     "Color": "blue",
                     "Filled": "true",
                     "Layer": 0,
                     "r": 0.8}
    elif type(agent) is ExitAgent :
        portrayal = {"Shape": "images/emergency.png",
                     "Color": "green",
                     "w": 0.8,
                     "h": 0.8,
                     "Filled": "true",
                     "Layer": 0,
                     "r": 0.8}
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
