import enum

from mesa import Agent

from percept import Percept
from model import NuclearWasteModel
from agent import AgentColor


class Action(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    TAKE = 4
    DROP = 5
    MERGE = 6
    STAY = 7

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def to_dict(self):
        return self.name

    @staticmethod
    def from_dict(d):
        return Action[d]

    @staticmethod
    def from_int(i):
        return Action(i)


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


def move_agent(agent: Agent, action: Action, environment: NuclearWasteModel):
    pos = agent.pos
    if action == Action.LEFT:
        if stays_in_area((pos[0] - 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] - 1, pos[1]))
        return Percept(
            radiactivity=environment.get_radiactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0] - 1, pos[1]),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.RIGHT:
        if stays_in_area((pos[0] + 1, pos[1]), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0] + 1, pos[1]))
        return Percept(
            radiactivity=environment.get_radiactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0] + 1, pos[1]),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.UP:
        if stays_in_area((pos[0], pos[1] + 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] + 1))
        return Percept(
            radiactivity=environment.get_radiactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0], pos[1] + 1),
            other_on_pos=environment.others_on_pos(agent),
        )
    elif action == Action.DOWN:
        if stays_in_area((pos[0], pos[1] - 1), environment, agent.color):
            agent.model.grid.move_agent(agent, (pos[0], pos[1] - 1))
        return Percept(
            radiactivity=environment.get_radiactivity(pos),
            waste1=None,
            waste2=None,
            pos=(pos[0], pos[1] - 1),
            other_on_pos=environment.others_on_pos(agent),
        )
    else:
        raise ValueError("Unknown action: {}".format(action))


def take(agent: Agent, environment: NuclearWasteModel):
    pass


def drop(agent: Agent, environment: NuclearWasteModel):
    pass


def merge(agent: Agent, environment: NuclearWasteModel):
    pass


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
    agent: Agent, action: Action, environment: NuclearWasteModel
) -> Percept:
    """Executes the corresponding handler based on the action."""
    action_enum = Action(action)
    handler = get_action_handler(action_enum)
    return handler(agent, environment)