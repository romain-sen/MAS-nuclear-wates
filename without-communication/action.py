from object import WasteAgent
from types_1 import Action, AgentColor, Percept, NuclearWasteModel, CleaningAgent


def stays_in_area(pos, environment, color: AgentColor):
    """
    Check if the agent remains within its designated area based on its color.

    Each color (GREEN, YELLOW, RED) has a different right boundary within the grid.
    - GREEN agents are limited to the first third of the grid width.
    - YELLOW agents are limited to the first two-thirds.
    - RED agents can move throughout the grid width.

    Parameters:
    - pos (tuple): The (x, y) position of the agent.
    - environment (Environment): The environment object containing the grid.
    - color (AgentColor): The color of the agent, determining its allowed area.

    Returns:
    - bool: True if the agent stays in the valid area, False otherwise.
    """

    # Vertical boundaries are the same for all agents.
    within_vertical_limits = 0 < pos[1] < environment.grid.height - 1

    # Horizontal boundaries depend on the agent's color.
    right_boundaries = {
        AgentColor.GREEN: environment.grid.width // 3 - 1,
        AgentColor.YELLOW: 2 * environment.grid.width // 3 - 1,
        AgentColor.RED: environment.grid.width - 1,
    }
    within_horizontal_limits = 0 < pos[0] < right_boundaries[color]

    return within_vertical_limits and within_horizontal_limits


def move_agent(agent: CleaningAgent, action: Action, environment):
    pos = agent.pos
    if action == Action.LEFT:
        if stays_in_area((pos[0] - 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] - 1, pos[1]))
        return Percept(
            radiactivity=environment.get_radioactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0] - 1, pos[1]),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.RIGHT:
        if stays_in_area((pos[0] + 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] + 1, pos[1]))
        return Percept(
            radiactivity=environment.get_radioactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0] + 1, pos[1]),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.UP:
        if stays_in_area((pos[0], pos[1] + 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] + 1))
        return Percept(
            radiactivity=environment.get_radioactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0], pos[1] + 1),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.DOWN:
        if stays_in_area((pos[0], pos[1] - 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] - 1))
        return Percept(
            radiactivity=environment.get_radioactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0], pos[1] - 1),
            other_on_pos=environment.others_on_pos(agent),
        )
    else:
        raise ValueError("Unknown action: {}".format(action))


def take(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()
    # Get the waste agent at the agent's position
    cell_content = environment.grid.get_cell_list_contents([agent.pos])
    waste_agents = [obj for obj in cell_content if isinstance(obj, WasteAgent)]
    if waste_agents:
        # Pick the first waste agent found
        waste_agent = waste_agents[0]
        try:
            environment.give_waste_agent(
                waste_agent.unique_id, waste_agent.color, agent.unique_id
            )
            if last_percept.waste1 is None:
                percept = Percept(
                    radiactivity=environment.get_radioactivity(agent.pos),
                    waste1=waste_agent,
                    waste2=None,
                    pos=agent.pos,
                    other_on_pos=environment.others_on_pos(agent),
                )
            else:
                percept = Percept(
                    radiactivity=environment.get_radioactivity(agent.pos),
                    waste1=last_percept.waste1,
                    waste2=waste_agent,
                    pos=agent.pos,
                    other_on_pos=environment.others_on_pos(agent),
                )
            return percept
        except Exception as e:
            print(e)
            return last_percept
    return last_percept


def drop(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()
    try:
        # TODO: Drop the first waste of the list
        waste_id = last_percept.waste1.unique_id
        environment.drop_waste(waste_id, agent.unique_id, agent.pos)
        return Percept(
            radiactivity=environment.get_radioactivity(agent.pos),
            waste1=None,
            waste2=last_percept.waste2,
            pos=agent.pos,
            other_on_pos=environment.others_on_pos(agent),
        )
    except Exception as e:
        print(e)
        return last_percept


def merge(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()
    try:
        new_waste = environment.merge_wastes(
            last_percept.waste1.unique_id,
            last_percept.waste2.unique_id,
            agent.unique_id,
        )
        # Update the percept with the new waste
        return Percept(
            radiactivity=environment.get_radioactivity(agent.pos),
            waste1=new_waste,
            waste2=None,
            pos=agent.pos,
            other_on_pos=environment.others_on_pos(agent),
        )
    except Exception as e:
        print(e)
        return last_percept


def get_action_handler(action: Action):
    """Maps each action to its corresponding handler."""
    action_mapping = {
        Action.LEFT: (
            lambda agent, environment: move_agent(agent, Action.LEFT, environment)
        ),
        Action.RIGHT: (
            lambda agent, environment: move_agent(agent, Action.RIGHT, environment)
        ),
        Action.UP: (
            lambda agent, environment: move_agent(agent, Action.UP, environment)
        ),
        Action.DOWN: (
            lambda agent, environment: move_agent(agent, Action.DOWN, environment)
        ),
        Action.TAKE: take,
        Action.DROP: drop,
        Action.MERGE: merge,
    }

    handler = action_mapping.get(action, None)
    if handler is None:
        raise NotImplementedError(f"No handler implemented for {action}")
    return handler


def handle_action(
    agent: CleaningAgent, action: Action, environment: NuclearWasteModel
) -> Percept:
    """Executes the corresponding handler based on the action."""
    handler = get_action_handler(action=action)
    return handler(agent, environment)
