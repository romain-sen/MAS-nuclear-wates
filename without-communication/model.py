import random

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from object import RadioactivityAgent, WasteAgent
from action import handle_action
from agent import RandomCleaningAgent, CleaningAgent

from types_1 import AgentColor, PickedWastes
from typing import List


def find_picked_waste_by_id(waste_id: int, picked_wastes_list: List[PickedWastes]):
    """
    Find a PickedWastes object in a list by its wasteId.

    :param waste_id: The wasteId to search for.
    :param picked_wastes_list: The list of PickedWastes objects.
    :return: The PickedWastes object with the matching wasteId, or None if not found.
    """
    for picked_waste in picked_wastes_list:
        if picked_waste.wasteId == waste_id:
            return picked_waste
    return None


class NuclearWasteModel(Model):
    """
    The environment of the model.
    """

    def __init__(self, N_AGENTS, N_WASTES, width, height):
        super().__init__()
        self.num_agents = N_AGENTS
        self.num_wastes = N_WASTES
        self.grid = MultiGrid(width, height, True)
        self.picked_wastes_list: List[PickedWastes] = []

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
        waste_agents = [
            obj for obj in cell_content if isinstance(obj, RadioactivityAgent)
        ]
        if waste_agents != []:
            return waste_agents[0].indicate_radioactivity()
        return 0

    def get_who_picked_waste(self, waste_id: int) -> int:
        """
        Get the agent who picked the waste.
        Return -1 if the waste is not picked.
        """
        picked_waste = find_picked_waste_by_id(waste_id, self.picked_wastes_list)
        if picked_waste is None:
            return -1
        return picked_waste.agentId

    def give_waste_agent(self, waste_id: int, waste_color, agent_id: int):
        """
        Give the waste to the agent.
        """
        # Check if the waste is already picked
        picked_waste = find_picked_waste_by_id(waste_id, self.picked_wastes_list)
        if picked_waste is not None:
            raise Exception("Waste already picked.")
        # Add the waste to the picked wastes list of the environment
        self.picked_wastes_list.append(
            PickedWastes(agentId=agent_id, wasteId=waste_id, wasteColor=waste_color)
        )
        # Remove the waste from the grid
        waste = self.grid.get_cell_list_contents([self.grid.coord_iter()])[waste_id]
        self.grid.remove_agent(waste)

    def drop_waste(self, waste_id: int, agent_id: int, pos: tuple[int, int]):
        """
        Drop the waste from the agent.
        """
        waste = find_picked_waste_by_id(waste_id, self.picked_wastes_list)
        # If no waste, raise an exception
        if waste is None:
            raise Exception("No waste to drop.")
        # Add the waste to the grid
        waste_agent = WasteAgent(waste.wasteId, waste.wasteColor, self)
        self.grid.place_agent(waste_agent, pos)
        self.schedule.add(waste_agent)
        # Remove the waste of the picked wastes list of the environment
        self.picked_wastes_list.remove(waste)

    def merge_wastes(self, waste_id1: int, waste_id2: int, agent_id: int) -> WasteAgent:
        """
        Merge the two wastes into a new one and return it.
        If the two wastes are of different colors or one of them is red, raise an exception.
        2 green -> 1 yellow
        2 yellow -> 1 red
        """
        waste1 = find_picked_waste_by_id(waste_id1, self.picked_wastes_list)
        waste2 = find_picked_waste_by_id(waste_id2, self.picked_wastes_list)
        # Check if the two wastes are the same color, and the color is not red
        if (
            waste1["wasteColor"] != waste2["wasteColor"]
            or waste1["wasteColor"] == AgentColor.RED
        ):
            raise Exception(
                "Cannot merge wastes of different colors or with red waste."
            )

        if waste1["wasteColor"] == AgentColor.GREEN:
            waste_color = AgentColor.YELLOW
        else:
            waste_color = AgentColor.RED

        # Remove the two wastes from the picked wastes list of the environment
        self.picked_wastes_list.remove(waste1)
        self.picked_wastes_list.remove(waste2)

        # Add the new waste to the picked wastes list of the environment, taking the first id
        self.picked_wastes_list.append(
            PickedWastes(agentId=agent_id, wasteId=waste_id1, wasteColor=waste_color)
        )
        return WasteAgent(waste_id1, waste_color, self)
