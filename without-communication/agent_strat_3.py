from mesa import Agent

from action import Action
from agent import CleaningAgent
from types_1 import AgentColor


class GreenCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        """
        The strategy of the green agent is to move randomly and take a waste if it find one.
        Then, it brings the waste to the top row, at its rightmost position allowed (x_max), and drops it.
        But if at this place, there already is a green waste, it takes it and merges it with the waste it is carrying, then drops it.
        """
        last_percept = self.give_last_percept()
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        action = movables[self.random.randrange(len(movables))]

        is_on_green_deposit = (
            last_percept["pos"][1] == self.knowledge["grid_height"] - 1
            and self.pos[0] == self.knowledge["x_max"] - 1
        )

        print("State : ", last_percept)
        print(
            "Waste in hand : ",
            last_percept["wastes"][0] if len(last_percept["wastes"]) > 0 else None,
        )

        # If Agent is on the "deposit green" cell, so the top and rightmost green corner
        if is_on_green_deposit:
            # If he has a waste, and there is a waste on the cell of the same color, and has free spot, take it
            if (
                len(last_percept["wastes"]) == 1
                and last_percept["waste_on_pos"] == AgentColor.GREEN
            ):
                action = Action.TAKE
            else:
                # If he has a waste, and there is a waste on the cell, drop it
                if len(last_percept["wastes"]) > 0:
                    action = Action.DROP

        # If the agent is on a waste, take it if not already carrying the maximum waste allowed
        if (
            self.model.is_on_waste(self.pos) is AgentColor.GREEN
            and len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
            and not is_on_green_deposit
        ):
            action = Action.TAKE

        # If carrying a waste, move to top row at the rightmost allowed position
        if len(last_percept["wastes"]) > 0:
            if (
                self.pos[1] < self.knowledge["grid_height"] - 1
            ):  # if not at the top row, move up
                action = Action.UP
            else:
                if (
                    self.pos[0] < self.knowledge["x_max"] - 1
                ):  # if not at the x_max position, move right
                    action = Action.RIGHT

        # If the agent has two wastes, merge them  --  last condition so can override other actions
        if len(last_percept["wastes"]) == 2:
            if (
                last_percept["wastes"][0].indicate_color()
                == last_percept["wastes"][1].indicate_color()
            ):
                action = Action.MERGE

        print("Action : ", action)
        return action


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
        x_max = environment.grid.width
        if agent_color == AgentColor.GREEN:
            x_max = environment.grid.width // 3
            x = environment.random.randrange(environment.grid.width // 3)
        y = environment.random.randrange(environment.grid.height)

        # Create and add the agent to the environment.
        agent = GreenCleaningAgent(
            unique_id=environment.obj_id,
            color=agent_color,
            x_max=x_max,
            model=environment,
        )
        environment.schedule.add(agent)
        environment.grid.place_agent(agent, (x, y))


def add_agents_strat_3(environment, n_green_agents, n_yellow_agents, n_red_agents):
    """
    Add agents to the environment.
    """
    add_cleaning_agents(environment, n_green_agents, AgentColor.GREEN)
