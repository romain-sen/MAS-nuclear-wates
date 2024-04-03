from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from model import NuclearWasteModel
from object import WasteAgent, RadioactivityAgent
from agent import RandomCleaningAgent
from types_1 import AgentColor


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Color": "red",
        "Layer": 0,
        "r": 0.5,
    }
    if isinstance(agent, WasteAgent):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.5
        portrayal["h"] = 0.5
        portrayal["Color"] = agent.indicate_color().__str__()
    elif isinstance(agent, RadioactivityAgent):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Color"] = "gray"
    elif isinstance(agent, RandomCleaningAgent):
        portrayal["Color"] = agent.color.__str__()
        portrayal["r"] = 0.3

    return portrayal


width = 12
height = 10
n_agents = 3
n_wastes = 3
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)
server = ModularServer(
    NuclearWasteModel,
    [grid],
    "NuclearWasteModel",
    {"N_AGENTS": n_agents, "N_WASTES": n_wastes, "width": width, "height": height},
)
server.port = 8521  # The default
server.reset_model()
server.launch()
