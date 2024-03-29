from mesa import Agent


class RadioactivityAgent(Agent):
    def __init__(self, unique_id, radioactivity, model):
        super().__init__(unique_id, radioactivity, model)
        self.radioactivity = radioactivity

    def step(self):
        pass

    def indicate_radioactivity(self):
        return self.radioactivity


class WasteAgent(Agent):
    def __init__(self, unique_id, color, model):
        super().__init__(unique_id, color, model)
        self.color = color

    def step(self):
        pass

    def indicate_color(self):
        return self.color
