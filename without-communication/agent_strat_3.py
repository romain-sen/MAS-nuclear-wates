from mesa import Agent

from action import Action
from agent import CleaningAgent
from types_1 import AgentColor


def define_step_between_checking(grid_height, grid_width):
    return grid_height * (grid_width // 3) // 3


def get_random_default_move(env):
    movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
    return movables[env.random.randrange(len(movables))]


def save_last_pos(self):
    if self.knowledge["have_saved_last_pos"] is False:
        self.knowledge["last_pos"] = self.pos
        self.knowledge["have_saved_last_pos"] = True


def return_to_last_pos(self):
    self.knowledge["go_back"] = True


def get_default_move(pos, x_min, x_max, grid_height, go_back=False, last_pos=None):
    x, y = pos

    # If go back is True, the agent will go back to the last position it was
    if go_back:
        last_x, last_y = last_pos
        if x < last_x:
            return Action.RIGHT
        elif x > last_x:
            return Action.LEFT
        elif y < last_y:
            return Action.UP
        elif y > last_y:
            return Action.DOWN

    almost_last_top_row = y == grid_height - 2
    not_almost_last_top_row = y < grid_height - 2
    last_top_row = y == grid_height - 1
    last_bottom_row = y == 0
    not_last_bottom_row = y > 0
    first_col = x == x_min
    last_col = x == x_max - 1
    odd_col = x % 2 == 1
    even_col = x % 2 == 0

    if last_top_row:
        if first_col:
            return Action.DOWN
        else:
            return Action.LEFT

    if even_col:
        if not_last_bottom_row:
            return Action.DOWN
        elif last_bottom_row:
            return Action.RIGHT

    if odd_col:
        if not_almost_last_top_row or (almost_last_top_row and last_col):
            return Action.UP
        elif almost_last_top_row:
            return Action.RIGHT

    print("Error in get_default_move")
    return Action.STAY


class GreenCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        """
        The strategy of the green agent is to move randomly and take a waste if it find one.
        Then, it brings the waste to the top row, at its rightmost position allowed (x_max), and drops it.
        But if at this place, there already is a green waste, it takes it and merges it with the waste it is carrying, then drops it.
        """
        last_percept = self.give_last_percept()
        action = get_default_move(
            self.pos,
            0,
            self.knowledge["x_max"],
            self.knowledge["grid_height"],
            self.knowledge["go_back"],
            self.knowledge["last_pos"],
        )

        is_on_green_deposit = (
            last_percept["pos"][1] == self.knowledge["grid_height"] - 1
            and self.pos[0] == self.knowledge["x_max"] - 1
        )
        is_on_yellow_deposit = (
            last_percept["pos"][1] == self.knowledge["grid_height"] - 2
            and self.pos[0] == self.knowledge["x_max"] - 1
        )

        waste_on_pos = self.model.is_on_waste(self.pos)
        first_waste_in_hand = (
            last_percept["wastes"][0] if len(last_percept["wastes"]) > 0 else None
        )
        second_waste_in_hand = (
            last_percept["wastes"][1] if len(last_percept["wastes"]) > 1 else None
        )
        has_free_spot = (
            len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
        )

        # If Agent is on the "deposit green" cell, so the top and rightmost green corner
        if is_on_green_deposit:
            # If he has a waste, and there is a waste on the cell of the same color, and has free spot, take it
            if len(last_percept["wastes"]) == 1 and waste_on_pos == AgentColor.GREEN:
                action = Action.TAKE
            else:
                # If he has a waste, and there is a waste on the cell, drop it
                if (
                    first_waste_in_hand is not None
                    and first_waste_in_hand.indicate_color() == AgentColor.GREEN
                ):
                    action = Action.DROP
                    return_to_last_pos(self)
                elif (
                    first_waste_in_hand is not None
                    and first_waste_in_hand.indicate_color() == AgentColor.YELLOW
                ):
                    action = Action.DOWN

        if is_on_yellow_deposit:
            if (
                first_waste_in_hand is not None
                and first_waste_in_hand.indicate_color() == AgentColor.YELLOW
            ):
                action = Action.DROP
                return_to_last_pos(self)
            elif (
                first_waste_in_hand is not None
                and first_waste_in_hand.indicate_color() == AgentColor.GREEN
            ):
                action = Action.UP

        # If the agent is on a waste, take it if not already carrying the maximum waste allowed
        if (
            waste_on_pos is AgentColor.GREEN
            and has_free_spot
            and not is_on_green_deposit
        ):
            action = Action.TAKE

        # If carrying a waste, move to top row at the rightmost allowed position
        if first_waste_in_hand is not None:
            if first_waste_in_hand.indicate_color() == AgentColor.GREEN:
                if (
                    self.pos[1] < self.knowledge["grid_height"] - 1
                ):  # if not at the top row, move up
                    action = Action.UP
                    # Save the last position to go back to it
                    save_last_pos(self)
                elif (
                    self.pos[0] < self.knowledge["x_max"] - 1
                ):  # if not at the x_max position, move right
                    action = Action.RIGHT
                    save_last_pos(self)

        # If the agent has two wastes, merge them  --  last condition so can override other actions
        if second_waste_in_hand is not None:
            if (
                last_percept["wastes"][0].indicate_color()
                == last_percept["wastes"][1].indicate_color()
            ):
                action = Action.MERGE

        return action


class YellowCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:

        last_percept = self.give_last_percept()
        x_green_zone = self.knowledge["grid_width"] // 3

        time_between_checking = define_step_between_checking(
            self.knowledge["grid_height"], self.knowledge["grid_width"]
        )

        action = None
        # This is the default action if no other action is taken
        action_default = get_default_move(
            self.pos,
            x_green_zone,
            self.knowledge["x_max"],
            self.knowledge["grid_height"],
            self.knowledge["go_back"],
            self.knowledge["last_pos"],
        )

        is_on_green_deposit = (
            self.pos[1] == self.knowledge["grid_height"] - 1
            and self.pos[0] == x_green_zone - 1
        )

        is_on_yellow_deposit = (
            self.pos[1] == self.knowledge["grid_height"] - 1
            and self.pos[0] == self.knowledge["x_max"] - 1
        )

        is_on_red_deposit = (
            self.pos[1] == self.knowledge["grid_height"] - 2
            and self.pos[0] == self.knowledge["x_max"] - 1
        )

        has_empty_hands = len(last_percept["wastes"]) == 0
        has_free_spot = (
            len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
        )
        waste_on_pos = self.model.is_on_waste(self.pos)

        first_waste_in_hand = (
            last_percept["wastes"][0] if len(last_percept["wastes"]) > 0 else None
        )
        second_waste_in_hand = (
            last_percept["wastes"][1] if len(last_percept["wastes"]) > 1 else None
        )

        # If the agent is on the green zone, move to the yellow one to work on it
        if self.pos[0] < x_green_zone:
            action = Action.RIGHT

        # Every time_between_checking steps, the agent moves to the green deposit if empty hands
        if self.step_count >= time_between_checking and has_empty_hands:
            if not is_on_green_deposit:
                if self.pos[0] >= x_green_zone:
                    action = Action.LEFT
                    save_last_pos(self)
                elif self.pos[1] < self.knowledge["grid_height"] - 1:
                    action = Action.UP
                    save_last_pos(self)
            # If is on the green deposit, and there is a waste, take it
            if is_on_green_deposit:
                self.step_count = 0
                return_to_last_pos(self)
                if waste_on_pos == AgentColor.YELLOW:
                    action = Action.TAKE
                # else:
                #     action = Action.STAY

        # If the agent has a waste
        if len(last_percept["wastes"]) > 0:
            # Go to the yellow deposit
            if not is_on_yellow_deposit:
                if self.pos[0] < self.knowledge["x_max"] - 1:
                    action = Action.RIGHT
                    save_last_pos(self)
                if self.pos[1] < self.knowledge["grid_height"] - 1:
                    action = Action.UP
                    save_last_pos(self)
        else:  # If the agent has no waste
            # If the agent is on a waste, take it
            if (
                self.model.is_on_waste(self.pos) is AgentColor.YELLOW
                # and len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"] # not necessary
                and not is_on_yellow_deposit
            ):
                action = Action.TAKE

        # If is on the yellow deposit
        if is_on_yellow_deposit:
            # If he has a waste, and there is a waste on the cell of the same color, and has free spot, take it
            if (
                has_free_spot
                and first_waste_in_hand is not None
                and waste_on_pos == AgentColor.YELLOW
            ):
                action = Action.TAKE
            else:
                # If he has a waste, and there is a waste on the cell, drop it
                if (
                    first_waste_in_hand is not None
                    and first_waste_in_hand.indicate_color() == AgentColor.YELLOW
                ):
                    action = Action.DROP
                    return_to_last_pos(self)
                elif (
                    first_waste_in_hand is not None
                    and first_waste_in_hand.indicate_color() == AgentColor.RED
                ):
                    action = Action.DOWN

        if is_on_red_deposit:
            if (
                first_waste_in_hand is not None
                and first_waste_in_hand.indicate_color() == AgentColor.RED
            ):
                action = Action.DROP
                return_to_last_pos(self)
            elif (
                first_waste_in_hand is not None
                and first_waste_in_hand.indicate_color() == AgentColor.YELLOW
            ):
                action = Action.UP

        # If the agent has two wastes, merge them  --  last condition so can override other actions
        if second_waste_in_hand is not None:
            if (
                last_percept["wastes"][0].indicate_color()
                == last_percept["wastes"][1].indicate_color()
            ):
                action = Action.MERGE

        if action is None:
            action = action_default
            if not self.knowledge["go_back"]:
                self.step_count += 1  # Only count the default actions
        return action


class RedCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:

        last_percept = self.give_last_percept()
        x_yellow_zone = 2 * self.knowledge["grid_width"] // 3

        time_between_checking = define_step_between_checking(
            self.knowledge["grid_height"], self.knowledge["grid_width"]
        )

        action = None
        # This is the default action if no other action is taken
        action_default = get_default_move(
            self.pos,
            x_yellow_zone,
            self.knowledge["x_max"],
            self.knowledge["grid_height"],
            self.knowledge["go_back"],
            self.knowledge["last_pos"],
        )

        is_on_red_deposit = (
            self.pos[1] == self.knowledge["grid_height"] - 1
            and self.pos[0] == self.knowledge["x_max"] - 1
        )

        is_on_yellow_deposit = (
            self.pos[1] == self.knowledge["grid_height"] - 2
            and self.pos[0] == x_yellow_zone - 1
        )

        has_empty_hands = len(last_percept["wastes"]) == 0
        waste_on_pos = self.model.is_on_waste(self.pos)

        # If the agent is on the yellow zone, move to the yellow one to work on it
        if self.pos[0] < x_yellow_zone:
            action = Action.RIGHT

        # Every time_between_checking steps, the agent moves to the yellow deposit if empty hands
        if self.step_count >= time_between_checking and has_empty_hands:
            if not is_on_yellow_deposit:
                if self.pos[0] >= x_yellow_zone:
                    action = Action.LEFT
                    save_last_pos(self)
                if self.pos[1] < self.knowledge["grid_height"] - 2:
                    action = Action.UP
                    save_last_pos(self)
            # If is on the yellow deposit, and there is a waste, take it
            if is_on_yellow_deposit:
                self.step_count = 0
                return_to_last_pos(self)
                if waste_on_pos == AgentColor.RED:
                    action = Action.TAKE
                # else:
                #     action = Action.STAY

        # If the agent has a waste
        if len(last_percept["wastes"]) > 0:
            # Go to the red deposit
            if not is_on_red_deposit:
                if self.pos[0] < self.knowledge["x_max"] - 1:
                    action = Action.RIGHT
                    save_last_pos(self)
                if self.pos[1] < self.knowledge["grid_height"] - 1:
                    action = Action.UP
                    save_last_pos(self)
        else:  # If the agent has no waste
            # If the agent is on a waste, take it if not already carrying the maximum waste allowed
            if (
                self.model.is_on_waste(self.pos) is AgentColor.RED
                and len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
                and not is_on_red_deposit
            ):
                action = Action.TAKE

        # If is on the red deposit
        if is_on_red_deposit:
            # If he has a waste, and there is a waste on the cell of the same color, and has free spot, take it
            if (
                len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
                and waste_on_pos == AgentColor.RED
            ):
                action = Action.TAKE
            else:
                # If he has a waste, and there is a waste on the cell, drop it
                if len(last_percept["wastes"]) > 0:
                    action = Action.DROP
                    return_to_last_pos(self)

        if action is None:
            action = action_default
            if not self.knowledge["go_back"]:
                self.step_count += 1
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

        y = environment.random.randrange(environment.grid.height)
        # Set movement boundaries based on the agent's color.
        x_max_green = environment.grid.width // 3
        x_max_yellow = 2 * environment.grid.width // 3
        x_max_red = environment.grid.width
        if agent_color == AgentColor.GREEN:
            x = environment.random.randrange(x_max_green)
            agent = GreenCleaningAgent(
                unique_id=environment.obj_id,
                color=agent_color,
                x_max=x_max_green,
                model=environment,
            )
        elif agent_color == AgentColor.YELLOW:
            x = environment.random.randrange(x_max_green, x_max_yellow)
            agent = YellowCleaningAgent(
                unique_id=environment.obj_id,
                color=agent_color,
                x_max=x_max_yellow,
                model=environment,
            )
        else:  # AgentColor.RED
            x = environment.random.randrange(x_max_yellow, x_max_red)
            agent = RedCleaningAgent(
                unique_id=environment.obj_id,
                color=agent_color,
                x_max=x_max_red,
                model=environment,
            )

        environment.schedule.add(agent)
        environment.grid.place_agent(agent, (x, y))


def add_agents_strat_3(environment, n_green_agents, n_yellow_agents, n_red_agents):
    """
    Add agents to the environment.
    """
    add_cleaning_agents(environment, n_green_agents, AgentColor.GREEN)
    add_cleaning_agents(environment, n_yellow_agents, AgentColor.YELLOW)
    add_cleaning_agents(environment, n_red_agents, AgentColor.RED)
