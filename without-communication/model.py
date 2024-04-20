from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from object import RadioactivityAgent, WasteAgent
from action import handle_action

from types_1 import (
    AgentColor,
    PickedWastes,
    DEPOSIT_RADIOACTIVITY,
    Neighboring,
    NeighboringType,
)
from agent import CleaningAgent
from typing import List
from utils import init_agents, find_picked_waste_by_id

import pandas as pd


def objects_to_strings(objects):
    return [str(obj) for obj in objects]


class NuclearWasteModel(Model):
    """
    The environment of the model.

    Parameters:
    - n_green_agents (int): The number of green cleaning agents in the model.
    - n_yellow_agents (int): The number of yellow cleaning agents in the model.
    - n_red_agents (int): The number of red cleaning agents in the model.
    - n_wastes (int): The total number of nuclear wastes in the model.
    - width (int): The width of the grid representing the environment.
    - height (int): The height of the grid representing the environment.
    - max_wastes_handed (int): The maximum number of wastes that an agent can carry at a time.
    """

    def __init__(
        self,
        n_green_agents=5,
        n_yellow_agents=5,
        n_red_agents=5,
        n_wastes=3,
        width=10,
        height=10,
        max_wastes_handed=2,
        upper_agent_proportion=0.5,
        strategy=1,
    ):
        super().__init__()

        self.grid = MultiGrid(width, height, True)
        self.num_agents = n_green_agents + n_yellow_agents + n_red_agents
        self.num_green_agents = n_green_agents
        self.num_yellow_agents = n_yellow_agents
        self.num_red_agents = n_red_agents
        self.num_wastes = n_wastes
        self.waste_remaining = n_wastes
        self.running = True
        self.height = height
        self.obj_id = 0
        self.max_wastes_handed = max_wastes_handed
        self.upper_agent_proportion = upper_agent_proportion
        self.strategy = strategy
        self.red_wastes_remaining = 0
        self.yellow_wastes_remaining = 0
        self.green_wastes_remaining = 0
        self.accessible_remaining_wastes = n_wastes
        self.is_finished = 0

        assert self.grid is not None, "Grid is not initialized."
        assert self.num_agents > 0, "Invalid number of agents."
        assert self.num_wastes >= 0, "Invalid number of wastes."

        self.max_wastes_handed = max_wastes_handed
        self.picked_wastes_list: List[PickedWastes] = []
        self.schedule = RandomActivation(self)

        # Create the data collector
        self.datacollector = DataCollector(
            agent_reporters={
                "Type": lambda a: type(a).__name__,
                "Color": "color",
                "Pos": "pos",
                "PickedWastes": (
                    lambda a: (
                        objects_to_strings(a.percept_temp["wastes"])
                        if hasattr(a, "percept_temp")
                        else []
                    )
                ),
            },
            model_reporters={
                "strategy": "strategy",
                # "picked_wastes": (lambda m: objects_to_strings(m.picked_wastes_list)),
                "waste_remaining": "waste_remaining",
                "red_wastes_remaining": "red_wastes_remaining",
                "yellow_wastes_remaining": "yellow_wastes_remaining",
                "green_wastes_remaining": "green_wastes_remaining",
                "accessible_remaining_wastes": "accessible_remaining_wastes",
                "is_finished": "is_finished",
            },
        )

        init_agents(
            self, n_green_agents, n_yellow_agents, n_red_agents, n_wastes, strategy
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if self.accessible_remaining_wastes == 0:
            self.is_finished += 1
            if self.is_finished == 1:
                print("All accessible wastes are cleaned.")

    def do(self, agent, action):
        return handle_action(agent=agent, action=action, environment=self)

    def get_agent_pos(self, agent_id: int):
        """
        Get the position of the agent.
        """
        # filter on the unique_id
        agent = [obj for obj in self.schedule.agents if obj.unique_id == agent_id]
        return agent[0].pos

    def others_on_pos(self, agent: CleaningAgent):
        """
        Check if there are other agents on the same position as the given agent.
        In the cell, there are at least 2 agents (the agent and the grid agent).
        """
        return len(self.grid.get_cell_list_contents([agent.pos])) > 2

    def is_on_waste(self, pos):
        """
        If there is a waste at this pos, return the waste's color.
        Else return None.
        """
        cell_content = self.grid.get_cell_list_contents([pos])
        waste_agents = [obj for obj in cell_content if isinstance(obj, WasteAgent)]
        if waste_agents != []:
            return waste_agents[0].indicate_color()
        return None

    def get_radioactivity(self, pos):
        """
        Get the radioactivity at the given position.
        """
        cell_content = self.grid.get_cell_list_contents([pos])
        radioactivity = [
            obj for obj in cell_content if isinstance(obj, RadioactivityAgent)
        ]
        if radioactivity != []:
            return radioactivity[0].indicate_radioactivity()
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

    def give_waste_agent(
        self, waste_id: int, waste_color, agent_id: int, pos: tuple[int, int]
    ):
        """
        Give the waste to the agent.
        """
        # Check if the waste is already picked
        picked_waste = find_picked_waste_by_id(waste_id, self.picked_wastes_list)
        if picked_waste is not None:
            raise Exception("Waste already picked.")
        # Check if the agent is already carrying two wastes
        if (
            len(
                [
                    waste
                    for waste in self.picked_wastes_list
                    if waste.agentId == agent_id
                ]
            )
            >= self.max_wastes_handed
        ):
            raise Exception(
                f"Agent {agent_id} cannot carry more than {self.max_wastes_handed} wastes."
            )

        # Add the waste to the picked wastes list of the environment
        self.picked_wastes_list.append(
            PickedWastes(agentId=agent_id, wasteId=waste_id, wasteColor=waste_color)
        )
        # Get all the agents on the position
        waste = self.grid.get_cell_list_contents([pos])
        if waste == []:
            raise Exception("Error while removing picked waste from the grid.")
        # Filter to get the waste agent and remove it
        waste = [obj for obj in waste if isinstance(obj, WasteAgent)]
        waste = waste[0]
        self.grid.remove_agent(waste)
        self.schedule.remove(waste)

    def drop_waste(self, waste_id: int, pos: tuple[int, int]):
        """
        Drop the waste from the agent.
        """
        waste = find_picked_waste_by_id(waste_id, self.picked_wastes_list)
        # If no waste, raise an exception
        if waste is None:
            raise Exception("No waste to drop.")

        # If a waste is dropped on the deposit zone,
        if pos == (
            self.grid.width - 1,
            self.grid.height - 1,
        ):
            # If the waste is red, it disappears
            if waste.wasteColor == AgentColor.RED:
                self.picked_wastes_list.remove(waste)
                self.waste_remaining -= 1
                self.accessible_remaining_wastes -= 1
                print(
                    f"Waste {waste_id} dropped on the deposit zone. Remaining wastes: {self.waste_remaining}"
                )
                return
            else:
                # If the waste is not red, it cannot be dropped on the deposit zone
                raise Exception("Cannot drop untransformed waste on the deposit zone.")

        # Add the waste to the grid
        waste_agent = WasteAgent(waste.wasteId, waste.wasteColor, self)
        self.grid.place_agent(waste_agent, pos)
        self.schedule.add(waste_agent)
        # Remove the waste of the picked wastes list of the environment
        self.picked_wastes_list.remove(waste)

    def merge_wastes(
        self, waste_id1: int, waste_id2: int, agent_id: int, pos: tuple[int, int]
    ) -> WasteAgent:
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
            waste1.wasteColor != waste2.wasteColor
            or waste1.wasteColor == AgentColor.RED
        ):
            raise Exception(
                "Cannot merge wastes of different colors or with red waste."
            )

        if waste1.wasteColor == AgentColor.GREEN:
            waste_color = AgentColor.YELLOW
        elif waste1.wasteColor == AgentColor.YELLOW:
            waste_color = AgentColor.RED
        else:
            raise Exception(
                "Cannot merge wastes of different colors or with red waste."
            )

        # Remove the two wastes from the picked wastes list of the environment
        self.picked_wastes_list.remove(waste1)
        self.picked_wastes_list.remove(waste2)

        new_id = self.obj_id + 1
        self.obj_id = new_id
        waste_merged = PickedWastes(
            agentId=agent_id, wasteId=new_id, wasteColor=waste_color
        )
        self.picked_wastes_list.append(waste_merged)

        self.waste_remaining -= 1
        self.accessible_remaining_wastes -= 1

        new_waste = WasteAgent(new_id, waste_color, self)
        # self.grid.place_agent(new_waste, self.get_agent_pos(agent_id))
        return new_waste

    def indicate_surroundings(self, pos):
        """
        Indicate the surroundings of the agent at the given position.

        Note : this function gives the surroundings of the agent at the given position, at a givent time.
        But the agent can move, so the surroundings can change. And in one step, all agents move, but not at the same time.
        So all agents can have different surroundings at the same time.
        """
        surrounding_agent = self.grid.get_neighbors(
            pos, moore=True, include_center=False
        )
        surrounding_objects: List[Neighboring] = []

        for agent in surrounding_agent:
            if isinstance(agent, CleaningAgent):
                surrounding_objects.append(
                    Neighboring(
                        type=NeighboringType.AGENT,
                        agentColor=agent.indicate_color(),
                        pos=agent.pos,
                    )
                )
            elif isinstance(agent, WasteAgent):
                surrounding_objects.append(
                    Neighboring(
                        type=NeighboringType.WASTE,
                        agentColor=agent.indicate_color(),
                        pos=agent.pos,
                    )
                )
            elif isinstance(agent, RadioactivityAgent):
                if agent.indicate_radioactivity() == DEPOSIT_RADIOACTIVITY:
                    surrounding_objects.append(
                        Neighboring(
                            type=NeighboringType.DEPOSIT,
                            agentColor=None,
                            pos=agent.pos,
                        )
                    )
        return surrounding_objects
