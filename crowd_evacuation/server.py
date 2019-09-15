from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter


def agent_portrayal(agent):
    portrayal = {"Shape": "images/sheep2.png",
                 "Layer": 0,
                 "scale": 1.5,
                 "r": 0.5}

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
