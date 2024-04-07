from typing import List
import random

from types_1 import (
    AgentColor,
    DEPOSIT_RADIOACTIVITY,
    PickedWastes,
)
from agent import RandomCleaningAgent, DefaultAgent
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


def initialize_wastes(environment, wastes_distribution):
    """
    Initializes the wastes in the environment based on the given distribution.

    Args:
        environment (Environment): The environment object.
        wastes_distribution (int): The distribution of wastes, ranging from 0 to 10.

    Raises:
        ValueError: If the wastes_distribution is not between 0 and 10.

    Notes:
        - The wastes_distribution determines the ratio of green, yellow, and red wastes.
        - When wastes_distribution is 0, most of the wastes are green and least are red.
        - When wastes_distribution is 10, most of the wastes are red and least are green.
        - The counts of green and yellow wastes are ensured to be even numbers.
        - The total number of wastes does not exceed the environment's num_wastes.
        - Any remaining wastes are allocated to yellow, adjusting to make it even if necessary.
    """
    if not 0 <= wastes_distribution <= 10:
        raise ValueError("wastes_distribution must be between 0 and 10.")

    green_ratio = (10 - wastes_distribution) / 10
    red_ratio = wastes_distribution / 10

    # Determine counts - ensuring green and yellow counts are even numbers.
    num_green = max(0, round(environment.num_wastes * green_ratio // 2) * 2)
    num_red = max(0, round(environment.num_wastes * red_ratio // 2) * 2)

    # Ensure total does not exceed environment.num_wastes.
    # Allocate remainder to yellow, adjusting to make it even if necessary.
    num_yellow = environment.num_wastes - num_green - num_red
    if num_yellow % 2 != 0:
        if num_green < num_red:
            num_yellow -= 1
            num_green += 2
        else:  # num_green >= num_red
            num_yellow += 1
            num_red -= 1

    for _ in range(environment.num_wastes):
        environment.obj_id += 1
        y = environment.random.randrange(environment.grid.height)
        if num_green > 0:
            color = AgentColor.GREEN
            x = environment.random.randrange(environment.grid.width // 3)
            num_green -= 1
        elif num_yellow > 0:
            color = AgentColor.YELLOW
            x = environment.random.randrange(
                environment.grid.width // 3, 2 * environment.grid.width // 3
            )
            num_yellow -= 1
        else:
            color = AgentColor.RED
            # Ensure no wastes are placed on the deposit zone
            if y == environment.grid.height - 1:
                x = environment.random.randrange(
                    2 * environment.grid.width // 3, environment.grid.width - 1
                )
            else:
                x = environment.random.randrange(
                    2 * environment.grid.width // 3, environment.grid.width
                )
        waste_agent = WasteAgent(environment.obj_id, color, environment)
        environment.schedule.add(waste_agent)
        environment.grid.place_agent(waste_agent, (x, y))


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
    initialize_wastes(environment, environment.wastes_distribution)

    # Add the cleaning agents
    add_cleaning_agents(environment, environment.num_green_agents, AgentColor.GREEN)
    add_cleaning_agents(environment, environment.num_yellow_agents, AgentColor.YELLOW)
    add_cleaning_agents(environment, environment.num_red_agents, AgentColor.RED)
