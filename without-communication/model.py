import random

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from object import RadioactivityAgent, WasteAgent
from action import handle_action


class NuclearWasteModel(Model):
    """
    The environment of the model.
    """

    def __init__(self, N_AGENTS, N_WASTES, width, height):
        super().__init__()
        self.num_agents = N_AGENTS
        self.num_wastes = N_WASTES
        self.grid = MultiGrid(width, height, True)

        # TODO : Move schedule to the schedule.py
        self.schedule = RandomActivation(self)

        # TODO : Add datacollector

        # Start with the radioactivity agents and place them all over the grid by zone (3 zones)
        id = 0
        # Zone 1 (West): radiactivity from 0 to 0.33
        for i in range(self.grid.width // 3):
            a = RadioactivityAgent(id, random.uniform(0, 0.33), self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width // 3)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            id += 1

        # Zone 2 (Middle): radiactivity from 0.33 to 0.66
        for i in range(self.grid.width // 3, 2 * self.grid.width // 3):
            a = RadioactivityAgent(i, random.uniform(0.33, 0.66), self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width // 3, 2 * self.grid.width // 3)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            id += 1

        # Zone 3 (East): radiactivity from 0.66 to 1
        for i in range(2 * self.grid.width // 3, self.grid.width):
            a = RadioactivityAgent(i, random.uniform(0.66, 1), self)
            self.schedule.add(a)
            x = self.random.randrange(2 * self.grid.width // 3, self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            id += 1

        # TODO : change the probability of the wastes to be placed in the grid (more on the west)
        id = 0
        for i in range(self.num_objects):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            if x < self.grid.width // 3:
                a = WasteAgent(id, "green", self)
            elif x < 2 * self.grid.width // 3:
                a = WasteAgent(id, "yellow", self)
            else:
                a = WasteAgent(id, "red", self)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))
            id += 1

    def step(self):
        self.schedule.step()
        # TODO : collect data

    def perceive(self, agent):
        pass
        # TODO : implement the perceive method

    def do(self, agent, action):
        return handle_action(agent, action, self)
