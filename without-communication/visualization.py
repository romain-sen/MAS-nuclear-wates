from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from model import NuclearWasteModel
from object import WasteAgent, RadioactivityAgent
from agent import DefaultAgent
from types_1 import AgentColor, DEPOSIT_RADIOACTIVITY


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "red",
        "Layer": 0,
        "r": 0.5,
    }
    if isinstance(agent, WasteAgent):
        color_map = {
            AgentColor.RED: "#E10B0B",
            AgentColor.YELLOW: "#EFF700",
            AgentColor.GREEN: "#1EA70B",
        }
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5
        portrayal["Color"] = color_map[agent.color]
    elif isinstance(agent, RadioactivityAgent):
        if agent.radioactivity == DEPOSIT_RADIOACTIVITY:
            portrayal["Color"] = "#0025F7"
        else:
            portrayal["Color"] = "#9FA2A5"
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
    elif isinstance(agent, DefaultAgent):
        color_map = {
            AgentColor.RED: "#E10B0B",
            AgentColor.YELLOW: "#EFF700",
            AgentColor.GREEN: "#1EA70B",
        }
        portrayal["Filled"] = "true"
        portrayal["Color"] = color_map[agent.color]
        portrayal["Layer"] = 1
        portrayal["r"] = 0.3

    return portrayal


width = 12
height = 10
n_agents = 3
n_wastes = 3
grid = CanvasGrid(agent_portrayal, width, height, width * 50, height * 50)
server = ModularServer(
    NuclearWasteModel,
    [grid],
    "NuclearWasteModel",
    {"N_AGENTS": n_agents, "N_WASTES": n_wastes, "width": width, "height": height},
)
server.port = 8521  # The default
server.reset_model()
server.launch()
