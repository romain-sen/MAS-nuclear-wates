from typing import List
import random

from types_1 import (
    AgentColor,
    DEPOSIT_RADIOACTIVITY,
    PickedWastes,
)
from agent import RandomCleaningAgent, DefaultAgent, UpperLineAgent
from object import RadioactivityAgent, WasteAgent


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


def initialize_wastes(environment):
    """
    Initialize the wastes in the environment.
    """
    for _ in range(environment.num_wastes):
        environment.obj_id += 1
        waste_color = random.choices(
            [AgentColor.GREEN, AgentColor.YELLOW, AgentColor.RED],
            weights=[0.4, 0.3, 0.3],
        )[0]
        if waste_color == AgentColor.GREEN:
            x = environment.random.randrange(environment.grid.width // 3)
        elif waste_color == AgentColor.YELLOW:
            x = environment.random.randrange(
                environment.grid.width // 3, 2 * environment.grid.width // 3
            )
        else:  # AgentColor.RED
            x = environment.random.randrange(2 * environment.grid.width // 3)
        y = environment.random.randrange(environment.grid.height)
        waste = WasteAgent(
            unique_id=environment.obj_id, color=waste_color, model=environment
        )
        environment.schedule.add(waste)
        environment.grid.place_agent(waste, (x, y))


def add_cleaning_agents(environment, num_agents: int, agent_color: AgentColor):
    """
    Adds cleaning agents to the environment.

    :param environment: The environment where agents are added.
    :param num_agents: The number of agents to add.
    :param agent_color: The specific color for all agents; if None, assigns random colors.
    """
    for i in range(num_agents):
        environment.obj_id += 1

        # Set movement boundaries based on the agent's color.
        if agent_color == AgentColor.RED:
            x = environment.random.randrange(
                2 * environment.grid.width // 3, environment.grid.width
            )
        elif agent_color == AgentColor.YELLOW:
            x = environment.random.randrange(
                environment.grid.width // 3, 2 * environment.grid.width // 3
            )
        else:  # AgentColor.GREEN
            x = environment.random.randrange(0, environment.grid.width // 3)

        y = environment.random.randrange(environment.grid.height)

        # Create and add the agent to the environment.
        agent = DefaultAgent(
            unique_id=environment.obj_id, color=agent_color, x_max=x, model=environment
        )
        environment.schedule.add(agent)
        environment.grid.place_agent(agent, (x, y))


def add_upper_agents(environment, num_agents: int):
    for i in range(num_agents):
        environment.obj_id += 1

        # Set movement boundaries based on the agent's color.
        x = environment.random.randrange(environment.grid.width)
        y = environment.random.randrange(environment.grid.height)

        # Create and add the agent to the environment.
        agent = UpperLineAgent(
            unique_id=environment.obj_id,
            color=AgentColor.RED,
            x_max=x,
            model=environment,
        )
        environment.schedule.add(agent)
        environment.grid.place_agent(agent, (x, y))


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
        (0.66, 0.99),
        environment,
        environment.obj_id,
    )

    # Add the wastes
    initialize_wastes(environment)

    # Add the cleaning agents
    add_cleaning_agents(environment, environment.num_green_agents, AgentColor.GREEN)
    add_cleaning_agents(environment, environment.num_yellow_agents, AgentColor.YELLOW)
    number_of_upper_agents = max(environment.num_red_agents // 2, 1)
    add_cleaning_agents(
        environment, environment.num_red_agents - number_of_upper_agents, AgentColor.RED
    )
    add_upper_agents(environment, number_of_upper_agents)
