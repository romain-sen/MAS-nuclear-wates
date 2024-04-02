import random

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from object import RadioactivityAgent, WasteAgent
from action import handle_action
from agent import RandomCleaningAgent, CleaningAgent

from types_1 import AgentColor


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

        # Add the wastes
        # TODO : change the probability of the wastes to be placed in the grid (more on the west)
        id = 0
        for i in range(self.num_wastes):
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

        # Add the cleaning agents
        for i in range(self.num_agents):
            color = random.choice(list(AgentColor))
            if color == AgentColor.RED:
                x = self.random.randrange(2 * self.grid.width // 3, self.grid.width)
            elif color == AgentColor.YELLOW:
                x = self.random.randrange(
                    self.grid.width // 3, 2 * self.grid.width // 3
                )
            else:
                x = self.random.randrange(self.grid.width // 3)
            y = self.random.randrange(self.grid.height)
            a = RandomCleaningAgent(unique_id=i, color=color, model=self)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        # TODO : collect data

    def perceive(self, agent):
        pass
        # TODO : implement the perceive method

    def do(self, agent, action):
        return handle_action(agent=agent, action=action, environment=self)

    def others_on_pos(self, agent: CleaningAgent):
        """
        Check if there are other agents on the same position as the given agent.
        """
        return len(self.grid.get_cell_list_contents([agent.pos])) > 1

    def get_radioactivity(self, pos):
        """
        Get the radioactivity at the given position.
        """
        cell_content = self.grid.get_cell_list_contents([pos])
        if cell_content:
            return cell_content[0].indicate_radioactivity()
        return 0
