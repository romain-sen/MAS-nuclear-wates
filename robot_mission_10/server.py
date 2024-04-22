import mesa
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from model import NuclearWasteModel
from object import WasteAgent, RadioactivityAgent
from agent import CleaningAgent
from types_1 import AgentColor, DEPOSIT_RADIOACTIVITY

MIN_COLOR_VALUE = 50  # The minimum color value for the radioactive color, to ensure it is visible and not black


def calculate_color_value(adjusted_value: float) -> int:
    """
    This function takes a float value between 0 and 0.33 as input and returns an integer between 0 and 255.
    The output integer is proportional to the input float value.

    Args:
        adjusted_value (float): A float value between 0 and 0.33.

    Returns:
        int: An integer between 0 and 255 proportional to the input float value.
    """
    if not 0 <= adjusted_value <= 0.33:
        raise ValueError(
            "adjusted_value must be between 0 and 0.33, got: " + str(adjusted_value)
        )

    color_value = int(adjusted_value * (255 / 0.33))
    # Calculate the inverse color value so darker is more radioactive
    color_value = 255 - color_value
    # Ensure the color_value is within MIN_COLOR_VALUE to 255
    color_value = max(MIN_COLOR_VALUE, min(color_value, 255))

    return color_value


def calculate_color(radioactivity: float) -> str:
    if radioactivity < 0.33:
        adjusted_value = radioactivity
        color_value = calculate_color_value(adjusted_value)
        return f"#00{color_value:02X}00"
    elif radioactivity < 0.66:
        adjusted_value = radioactivity - 0.33
        color_value = calculate_color_value(adjusted_value)
        return f"#{color_value:02X}{color_value:02X}00"
    else:
        adjusted_value = radioactivity - 0.66
        color_value = calculate_color_value(adjusted_value)
        return f"#{color_value:02X}0000"


def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, WasteAgent):
        if agent.color == AgentColor.RED:
            portrayal["Shape"] = (
                "without-communication/ressources/radioactive-waste-red.png"
            )
        elif agent.color == AgentColor.YELLOW:
            portrayal["Shape"] = (
                "without-communication/ressources/radioactive-waste-yellow2.jpg"
                # "without-communication/ressources/radioactive-waste-yellow.png"
                # "without-communication/ressources/radioactive-waste-red.png"
            )
        else:
            portrayal["Shape"] = (
                "without-communication/ressources/radioactive-waste-green.png"
            )
        portrayal["Layer"] = 1
        portrayal["scale"] = 0.8

    elif isinstance(agent, RadioactivityAgent):
        if agent.radioactivity == DEPOSIT_RADIOACTIVITY:
            portrayal["Color"] = "#0025F7"
        else:
            portrayal["Color"] = calculate_color(agent.radioactivity)

        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"

    elif isinstance(agent, CleaningAgent):
        if agent.color == AgentColor.GREEN:
            portrayal["Shape"] = "without-communication/ressources/green_robot.png"
        elif agent.color == AgentColor.YELLOW:
            portrayal["Shape"] = "without-communication/ressources/yellow_robot.png"
        else:
            portrayal["Shape"] = "without-communication/ressources/red_robot.png"
        portrayal["Layer"] = 2
        portrayal["scale"] = 0.9

    return portrayal


multiplicator = 5
width = 12 * multiplicator
height = 10 * multiplicator
size_pixel = 65 // multiplicator

model_params = {
    "n_green_agents": mesa.visualization.Slider("Green Agents", 1, 1, 5),
    "n_yellow_agents": mesa.visualization.Slider("Yellow Agents", 1, 1, 5),
    "n_red_agents": mesa.visualization.Slider("Red Agents", 1, 1, 5),
    "n_wastes": mesa.visualization.Slider("Wastes", 10, 1, 50),
    "max_wastes_handed": 2,
    "width": width,
    "height": height,
    "strategy": mesa.visualization.Choice(
        "Strategy",
        value=3,
        choices=[1, 3],
    ),
}

grid = CanvasGrid(
    agent_portrayal, width, height, width * size_pixel, height * size_pixel
)

chart = ChartModule(
    [{"Label": "waste_remaining", "Color": "Black"}],
    data_collector_name="datacollector",
)

server = ModularServer(
    NuclearWasteModel, [grid, chart], "NuclearWasteModel", model_params
)
server.port = 8521  # The default
server.reset_model()
server.launch()
