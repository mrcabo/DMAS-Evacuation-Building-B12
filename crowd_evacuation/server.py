from mesa.visualization.ModularVisualization import ModularServer
from .model import EvacuationModel
from mesa.visualization.modules import CanvasGrid
from crowd_evacuation.ChartVisualization import ChartModule
from crowd_evacuation.BarChartVisualization import BarChartModule
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import TextElement

from crowd_evacuation.exit_agent import ExitAgent
from crowd_evacuation.wall_agent import WallAgent
from crowd_evacuation.fire_agent import FireAgent
from crowd_evacuation.civilian_agent import CivilianAgent
from crowd_evacuation.steward_agent import StewardAgent
from crowd_evacuation.introduction_text import IntroductionText

COLORS_FIRE = {"On Fire": "#FF0000",
               "Burned Out": "#800000"}


class WarningUI(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        text = '<font color="red">' + model.warning_UI + '</font>'
        return text


class StatisticsTitle(TextElement):
    def __init__(self, text):
        self.text = text

    def render(self, model):
        return self.text


class StatisticsText(TextElement):
    def __init__(self):
        pass

    def render(self, model):
        text = ""
        count_agents = {}
        exit_list = [agent._exit_point for agent in model.agents_saved]
        for exit_pos in model.pos_exits:
            count_agents[exit_pos] = exit_list.count(exit_pos)
            text = text + "Number of agents saved through exit {} is: {}<br>".format(exit_pos, count_agents[exit_pos])
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
        if agent._age <= 45:
            portrayal["Color"] = "CornflowerBlue"
        else:
            portrayal["Color"] = "DarkBlue"
        portrayal["Filled"] = "true"
        portrayal["r"] = agent._weight / 100
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


line_chart = ChartModule([{"Label": "Agents killed", "Color": "red"},
                          {"Label": "Agents saved", "Color": "green"}])
labels = [(0, 5), (0, 25), (0, 45), (49, 14), (49, 15),
          (49, 16)]  # hardcoded for now, will not work if exits are changed
exits_barchart = BarChartModule([{"Label": "Exit {}".format(labels[0]), "Color": "green"},
                                 {"Label": "Exit {}".format(labels[1]), "Color": "green"},
                                 {"Label": "Exit {}".format(labels[2]), "Color": "green"},
                                 {"Label": "Exit {}".format(labels[3]), "Color": "green"},
                                 {"Label": "Exit {}".format(labels[4]), "Color": "green"},
                                 {"Label": "Exit {}".format(labels[5]), "Color": "green"}])
# demographics_agents_perished = PieChartModule([{},
#                                                {}])

introduction = IntroductionText()
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)
warnings = WarningUI()
title_statistics = StatisticsTitle("<h2 style='margin-top:50px'>Statistics</h2><br>")
statistics = StatisticsText()

model_legend = '''
 <fieldset>
  <legend style="font-size:16px; margin-top:20px;">Model Legend:</legend>
  <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:CornflowerBlue'></div> <p style="font-size:16px; margin-bottom: 15px">Agent aged <= 45 </p> </div>
  <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:DarkBlue'></div> <p style="font-size:16px; margin-bottom: 15px"> Agent aged > 45 </p> </div>
  <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:gold'></div> <p style="font-size:16px; margin-bottom: 15px"> Steward Agent </p> </div>
  <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:red'></div> <p style="font-size:16px; margin-bottom: 15px"> Fire </p> </div>
  <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:#800000'></div> <p style="font-size:16px; margin-bottom: 15px"> Burned out fire </p> </div>
   <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:green'></div> <p style="font-size:16px; margin-bottom: 15px"> Emergency exit </p> </div>
    <div><div style='float: left;height: 20px;width: 20px;margin-bottom: 15px;margin-right: 10px;border: 1px solid black;clear: both;background-color:black'></div><p style="font-size:16px; margin-bottom: 15px"> Wall </p> </div>
   </fieldset>
 '''

fire_starting_point = (1, 1)
model_params = {
    "N": UserSettableParameter('slider', "Number of civilian agents", 100, 1, 1000, 1,
                               description="Choose how many civilian agents to include in the model"),
    "K": UserSettableParameter('slider', "Number of steward agents", 0, 0, 30, 1,
                               description="Choose how many steward agents to include in the model"),
    "fire_x": UserSettableParameter('slider', "Fire starting point (x-coordinate)", 1, 1, 48, 1,
                                    description="Fire starting point (x-coordinate)"),
    "fire_y": UserSettableParameter('slider', "Fire starting point (y-coordinate)", 1, 1, 48, 1,
                                    description="Fire starting point (y-coordinate)"),
    "civil_info_exchange": UserSettableParameter('checkbox', 'Information exchange between civilians', value=True,
                                                 description="Choose whether civilians will exchange information with each other"),
    "Legend": UserSettableParameter('static_text', value=model_legend),

    "width": 50,
    "height": 50
}

server = ModularServer(EvacuationModel,
                       [introduction, warnings, grid, title_statistics,  line_chart, exits_barchart, statistics],
                       "Evacuation model",
                       model_params)
server.port = 8521
