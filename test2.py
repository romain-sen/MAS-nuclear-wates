from test import MoneyModel
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0,
        "Color": "red",
        "r": 0.5,
    }
    return portrayal


grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
server = ModularServer(
    MoneyModel,
    [grid],
    "Money Model",
    {"N_AGENTS": 10, "N_WASTES": 3, "width": 10, "height": 10},
)
server.port = 8521  # The default
server.launch()
