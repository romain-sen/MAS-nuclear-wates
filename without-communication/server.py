import mesa
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from model import NuclearWasteModel
from object import WasteAgent, RadioactivityAgent
from agent import DefaultAgent
from types_1 import AgentColor, DEPOSIT_RADIOACTIVITY

import matplotlib.colors as mcolors

def is_valid_color(hex_color):
    try:
        mcolors.to_rgba(hex_color)
        return True
    except ValueError:
        return False
    
def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, WasteAgent):
        if agent.color == AgentColor.RED:
            portrayal["Shape"] = "without-communication/ressources/radioactive-waste-red.png"
        elif agent.color == AgentColor.YELLOW:
            portrayal["Shape"] = "without-communication/ressources/radioactive-waste-yellow.png"
        else:
            portrayal["Shape"] = "without-communication/ressources/radioactive-waste-green.png"
        portrayal["Layer"] = 1
        portrayal["scale"] = 0.8
        

    elif isinstance(agent, RadioactivityAgent):
        if agent.radioactivity == DEPOSIT_RADIOACTIVITY:
            portrayal["Color"] = "#0025F7"
        else:
            if agent.radioactivity < 0.33:
                color_value = int(agent.radioactivity * 255)
                portrayal["Color"] = f'#00{color_value:02X}00'
                

            elif agent.radioactivity < 0.66:
                adjusted_value = (agent.radioactivity - 0.33) * 3  # Réajustement pour la plage jaune
                color_value = int(255 - adjusted_value * 255)
                portrayal["Color"] = f'#{color_value:02X}{color_value:02X}00'
                
            else:
                adjusted_value = min((agent.radioactivity - 0.66) * 3, 1)  # Réajustement pour la plage rouge
                color_value = int(255 - adjusted_value * 255)
                portrayal["Color"] = f'#{color_value:02X}0000'

        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"
        

    elif isinstance(agent, DefaultAgent):
        if agent.color == AgentColor.GREEN:
            portrayal["Shape"] = "without-communication/ressources/green_robot.png"
        elif agent.color == AgentColor.YELLOW:
            portrayal["Shape"] = "without-communication/ressources/yellow_robot.png"
        else:
            portrayal["Shape"] = "without-communication/ressources/red_robot.png"
        portrayal["Layer"] = 2
        portrayal["scale"] = 0.9
    
    return portrayal

width = 12
height = 10

model_params = {
    "n_green_agents": mesa.visualization.Slider("Green Agents", 3, 1, 5),
    "n_yellow_agents": mesa.visualization.Slider("Yellow Agents", 3, 1, 5),
    "n_red_agents": mesa.visualization.Slider("Red Agents", 3, 1, 5),
    "n_wastes": mesa.visualization.Slider("Wastes", 10, 1, 20),
    "wastes_distribution": mesa.visualization.Slider("Waste Distribution", 1, 1, 5),
    "max_wastes_handed": mesa.visualization.Slider("Max Wastes Handed", 2, 2, 2),
    "width": width,
    "height": height,
    }

grid = CanvasGrid(agent_portrayal, width, height, width*50, height*50)
server = ModularServer(NuclearWasteModel, [grid], "NuclearWasteModel", model_params)
server.port = 8521  # The default
server.reset_model()
server.launch()
