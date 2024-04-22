from object import WasteAgent
from types_1 import Action, AgentColor, Percept, NuclearWasteModel, CleaningAgent


def stays_in_area(pos, environment: NuclearWasteModel, color: AgentColor):
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
    within_vertical_limits = 0 <= pos[1] < environment.grid.height

    # Horizontal boundaries depend on the agent's color.
    right_boundaries = {
        AgentColor.GREEN: environment.grid.width // 3,
        AgentColor.YELLOW: 2 * environment.grid.width // 3,
        AgentColor.RED: environment.grid.width,
    }
    within_horizontal_limits = 0 <= pos[0] < right_boundaries[color]

    return within_vertical_limits and within_horizontal_limits


def move_agent(agent: CleaningAgent, action: Action, environment: NuclearWasteModel):
    last_percept = agent.give_last_percept()

    current_surroundings = environment.indicate_surroundings(agent.pos)
    new_default_percept = last_percept.copy()
    new_default_percept["surrounding"] = current_surroundings

    pos = agent.pos
    if action == Action.LEFT:
        if stays_in_area((pos[0] - 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] - 1, pos[1]))
            return Percept(
                radiactivity=environment.get_radioactivity(pos),
                wastes=last_percept["wastes"],
                pos=(pos[0] - 1, pos[1]),
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
        else:
            return new_default_percept
    elif action == Action.RIGHT:
        if stays_in_area((pos[0] + 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] + 1, pos[1]))
            return Percept(
                radiactivity=environment.get_radioactivity(pos),
                wastes=last_percept["wastes"],
                pos=(pos[0] + 1, pos[1]),
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
        else:
            return new_default_percept
    elif action == Action.UP:
        if stays_in_area((pos[0], pos[1] + 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] + 1))
            return Percept(
                radiactivity=environment.get_radioactivity(pos),
                wastes=last_percept["wastes"],
                pos=(pos[0], pos[1] + 1),
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
        else:
            return new_default_percept
    elif action == Action.DOWN:
        if stays_in_area((pos[0], pos[1] - 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] - 1))
            return Percept(
                radiactivity=environment.get_radioactivity(pos),
                wastes=last_percept["wastes"],
                pos=(pos[0], pos[1] - 1),
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
        else:
            return new_default_percept
    elif action == Action.STAY:
        return Percept(
            radiactivity=environment.get_radioactivity(pos),
            wastes=last_percept["wastes"],
            pos=pos,
            other_on_pos=environment.others_on_pos(agent),
            waste_on_pos=environment.is_on_waste(agent.pos),
            surrounding=current_surroundings,
        )
    else:
        raise ValueError("Unknown action: {}".format(action))


def take(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()

    current_surroundings = environment.indicate_surroundings(agent.pos)
    new_default_percept = last_percept.copy()
    new_default_percept["surrounding"] = current_surroundings

    # Get the waste agent at the agent's position
    cell_content = environment.grid.get_cell_list_contents([agent.pos])
    waste_agents = [obj for obj in cell_content if isinstance(obj, WasteAgent)]
    if waste_agents:
        # Pick the first waste agent found
        waste_agent = waste_agents[0]
        try:
            environment.give_waste_agent(
                waste_agent.unique_id, waste_agent.color, agent.unique_id, agent.pos
            )
            new_wastes = last_percept["wastes"]
            new_wastes.append(waste_agent)
            return Percept(
                radiactivity=environment.get_radioactivity(agent.pos),
                wastes=new_wastes,
                pos=agent.pos,
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
        except Exception as e:
            print(e)
            return new_default_percept
    else:
        return new_default_percept


def drop(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()

    current_surroundings = environment.indicate_surroundings(agent.pos)
    new_default_percept = last_percept.copy()
    new_default_percept["surrounding"] = current_surroundings

    try:
        if len(last_percept["wastes"]) > 0:
            waste_to_drop = last_percept["wastes"][0].unique_id
            environment.drop_waste(waste_to_drop, agent.pos)
            remaining_wastes = [
                waste
                for waste in last_percept["wastes"]
                if waste.unique_id != waste_to_drop
            ]
            return Percept(
                radiactivity=environment.get_radioactivity(agent.pos),
                wastes=remaining_wastes,
                pos=agent.pos,
                other_on_pos=environment.others_on_pos(agent),
                waste_on_pos=environment.is_on_waste(agent.pos),
                surrounding=current_surroundings,
            )
    except Exception as e:
        print(e)
        last_percept["surrounding"] = environment.indicate_surroundings(agent.pos)
        return new_default_percept


def merge(agent: CleaningAgent, environment: NuclearWasteModel):
    # Get the last percept of the agent
    last_percept = agent.give_last_percept()

    current_surroundings = environment.indicate_surroundings(agent.pos)
    new_default_percept = last_percept.copy()
    new_default_percept["surrounding"] = current_surroundings

    try:
        if len(last_percept["wastes"]) < 2:
            raise Exception("Not enough wastes to merge.")

        new_waste = environment.merge_wastes(
            waste_id1=last_percept["wastes"][0].unique_id,
            waste_id2=last_percept["wastes"][1].unique_id,
            agent_id=agent.unique_id,
            pos=agent.pos,
        )
        # Update the percept with the new waste
        return Percept(
            radiactivity=environment.get_radioactivity(agent.pos),
            wastes=[new_waste],
            pos=agent.pos,
            other_on_pos=environment.others_on_pos(agent),
            waste_on_pos=environment.is_on_waste(agent.pos),
            surrounding=current_surroundings,
        )
    except Exception as e:
        print(e)
        return new_default_percept


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
        Action.STAY: (
            lambda agent, environment: move_agent(agent, Action.STAY, environment)
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
