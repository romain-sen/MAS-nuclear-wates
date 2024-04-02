from model import NuclearWasteModel
import mesa.visualization

from types_1 import (
    WasteAgent,
    RadioactivityAgent,
    RandomCleaningAgent,
    AgentColor,
    NuclearWasteModel,
)


# def agent_portrayal(agent):
#     if agent is isinstance(agent, WasteAgent):
#         portrayal = {
#             "Shape": "circle",
#             "Filled": "true",
#             "Layer": 0,
#             "Color": agent.indicate_color(),
#             "r": 0.5,
#         }
#     elif agent is isinstance(agent, RadioactivityAgent):
#         portrayal = {
#             "Shape": "rect",
#             "Filled": "true",
#             "Layer": 0,
#             "Color": "blue",
#             "w": 1,
#             "h": 1,
#         }
#     elif agent is isinstance(agent, RandomCleaningAgent):
#         portrayal = {
#             "Shape": "rect",
#             "Filled": "true",
#             "Layer": 0,
#             "Color": agent.indicate_color(),
#             "w": 1,
#             "h": 1,
#         }
#     return portrayal


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "Color": "red",
        "r": 0.5,
    }
    return portrayal


width = 10
height = 10
n_agents = 3
n_wastes = 3
grid = mesa.visualization.CanvasGrid(
    agent_portrayal, width, height, width * 10, height * 10
)
server = mesa.visualization.ModularServer(
    NuclearWasteModel,
    [grid],
    "NuclearWasteModel",
    {"N_AGENTS": n_agents, "N_WASTES": n_wastes, "width": width, "height": height},
)
server.port = 8521  # The default
server.reset_model()
server.launch()
