import random

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from object import RadioactivityAgent, WasteAgent
from action import handle_action
from agent import DefaultAgent, CleaningAgent

from types_1 import AgentColor, PickedWastes, DEPOSIT_RADIOACTIVITY
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


def initialize_zone(start_x, end_x, radioactivity_range, environment, current_id):
    for i in range(start_x, end_x):
        for j in range(environment.grid.height):
            # Put deposit zone on the top right corner
            if i == environment.grid.width - 1 and j == environment.grid.height - 1:
                a = RadioactivityAgent(current_id, DEPOSIT_RADIOACTIVITY, environment)
            else:
                a = RadioactivityAgent(
                    current_id, random.uniform(*radioactivity_range), environment
                )
            environment.schedule.add(a)
            environment.grid.place_agent(a, (i, j))
            current_id += 1
    return current_id


def init_agents(environment):
    width_third = environment.grid.width // 3

    # Zone 1 (West): radioactivity from 0 to 0.33
    environment.obj_id = initialize_zone(
        0, width_third, (0, 0.33), environment, environment.obj_id
    )

    # Zone 2 (Middle): radioactivity from 0.33 to 0.66
    environment.obj_id = initialize_zone(
        width_third, 2 * width_third, (0.33, 0.66), environment, environment.obj_id
    )

    # Zone 3 (East): radioactivity from 0.66 to 1
    environment.obj_id = initialize_zone(
        2 * width_third,
        environment.grid.width,
        (0.66, 1),
        environment,
        environment.obj_id,
    )

    # Add the wastes
    # TODO : change the probability of the wastes to be placed in the grid (more on the west)
    for i in range(environment.num_wastes):
        environment.obj_id += 1
        x = environment.random.randrange(environment.grid.width)
        y = environment.random.randrange(environment.grid.height)
        if x < environment.grid.width // 3:
            a = WasteAgent(environment.obj_id, AgentColor.GREEN, environment)
        elif x < 2 * environment.grid.width // 3:
            a = WasteAgent(environment.obj_id, AgentColor.YELLOW, environment)
        else:
            a = WasteAgent(environment.obj_id, AgentColor.RED, environment)
        environment.schedule.add(a)
        environment.grid.place_agent(a, (x, y))

    # Add the cleaning agents
    for i in range(environment.num_agents):
        environment.obj_id += 1
        random_color = environment.random.choice(list(AgentColor))
        if random_color == AgentColor.RED:
            x_max = environment.grid.width
            x = environment.random.randrange(
                2 * environment.grid.width // 3, environment.grid.width
            )
        elif random_color == AgentColor.YELLOW:
            x_max = 2 * environment.grid.width // 3
            x = environment.random.randrange(
                environment.grid.width // 3, 2 * environment.grid.width // 3
            )
        else:
            x_max = environment.grid.width // 3
            x = environment.random.randrange(environment.grid.width // 3)
            y = environment.random.randrange(environment.grid.height)
        a = DefaultAgent(
            unique_id=environment.obj_id,
            color=random_color,
            x_max=x_max,
            model=environment,
        )
        environment.schedule.add(a)
        environment.grid.place_agent(a, (x, y))


class NuclearWasteModel(Model):
    """
    The environment of the model.
    """

    def __init__(self, N_AGENTS=3, N_WASTES=3, width=10, height=10):
        super().__init__()

        self.grid = MultiGrid(width, height, True)
        self.num_agents = N_AGENTS
        self.num_wastes = N_WASTES
        self.waste_remaining = N_WASTES
        self.running = True
        self.height = height
        self.obj_id = 0

        assert self.grid is not None, "Grid is not initialized."
        assert self.num_agents > 0, "Invalid number of agents."
        assert self.num_wastes >= 0, "Invalid number of wastes."

        self.picked_wastes_list: List[PickedWastes] = []

        # TODO : Move schedule to the schedule.py
        self.schedule = RandomActivation(self)

        # Create the data collector
        self.datacollector = DataCollector(
            agent_reporters={"Knowledge": "knowledge"},
            model_reporters={"PickedWastes": "picked_wastes_list"},
        )

        init_agents(self)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

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
        """
        return len(self.grid.get_cell_list_contents([agent.pos])) > 1

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
            >= 2
        ):
            raise Exception("Agent already carrying two wastes.")

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

        new_waste = WasteAgent(new_id, waste_color, self)
        # self.grid.place_agent(new_waste, self.get_agent_pos(agent_id))
        return new_waste
