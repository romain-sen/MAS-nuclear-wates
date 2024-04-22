from mesa import Agent
from types_1 import AgentColor, NuclearWasteModel


class RadioactivityAgent(Agent):
    def __init__(self, unique_id: int, radioactivity: float, model: NuclearWasteModel):
        super().__init__(unique_id, model)
        self.radioactivity = radioactivity

    def step(self):
        pass

    def indicate_radioactivity(self):
        return self.radioactivity

    def __str__(self) -> str:
        return f"RadioactivityAgent(id={self.unique_id}, radioactivity={self.radioactivity}, pos={self.pos})"


class WasteAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model: NuclearWasteModel):
        super().__init__(unique_id, model)
        self.color = color

    def step(self):
        pass

    def indicate_color(self):
        return self.color

    def __str__(self):
        return f"WasteAgent(id={self.unique_id}, color={self.color}, pos={self.pos})"
