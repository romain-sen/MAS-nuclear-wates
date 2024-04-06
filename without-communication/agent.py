from mesa import Agent

from action import Action
from types_1 import AgentColor, Knowledge, Percept, NuclearWasteModel


def update(knowledge: Knowledge, percepts: Percept, actions: Action):
    if percepts:
        knowledge["percepts"].append(percepts)
    if actions:
        knowledge["actions"].append(actions)


class CleaningAgent(Agent):
    def __init__(
        self, unique_id: int, color: AgentColor, x_max: int, model: NuclearWasteModel
    ):
        super().__init__(unique_id, model)
        self.color = color
        self.knowledge = {
            "actions": [],
            "percepts": [],
            "grid_width": self.model.grid.width,
            "grid_height": self.model.grid.height,
            "x_max": x_max,
            "max_wastes_handed": self.model.max_wastes_handed,
        }
        self.percept_temp = Percept(
            radiactivity=0,
            wastes=[],
            pos=(0, 0),
            other_on_pos=False,
            waste_on_pos=None,
        )
        self.action_temp = Action.STAY

    def deliberate(self) -> Action:
        pass

    def step(self):
        update(self.knowledge, self.percept_temp, self.action_temp)
        action = self.deliberate()
        self.action_temp = action
        self.percept_temp = self.model.do(self, action)

    def give_last_percept(self) -> Percept:
        return self.percept_temp

    def indicate_color(self):
        return self.color

    def __str__(self) -> str:
        return f"CleaningAgent(id={self.unique_id}, color={self.color}, pos={self.pos})"


class RandomCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        last_percept = self.give_last_percept()
        # If can pick a waste, do it
        if (
            self.model.is_on_waste(self.pos) is not None
            and len(last_percept["wastes"]) < self.knowledge["max_wastes_handed"]
        ):
            return Action.TAKE
        # Choose randomly an action to move
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        return movables[self.random.randrange(len(movables))]


class DefaultAgent(CleaningAgent):
    def deliberate(self) -> Action:
        last_percept = self.give_last_percept()
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        action = movables[self.random.randrange(len(movables))]
        # If the agent is on a waste, not on the top row and has a free spot, take it
        if (
            (last_percept["wastes"] is not None and len(last_percept["wastes"]) < 2)
            and self.model.is_on_waste(self.pos) is not None
            and last_percept["pos"][1] < self.model.height - 1
        ):
            # TODO : Check if the agent is on top without using the height of the grid
            action = Action.TAKE

        if len(last_percept["wastes"]) == 2:
            if (
                last_percept["wastes"][0].indicate_color()
                == last_percept["wastes"][1].indicate_color()
            ):
                action = Action.MERGE

        # If the agent has a waste, go up to drop it on the top row
        if len(last_percept["wastes"]) > 0 and action != Action.MERGE:
            if len(self.knowledge["percepts"]) > 1:
                # Try to go up first
                if self.action_temp != Action.UP:

                    if self.action_temp == Action.MERGE:
                        action = Action.DROP
                    else:
                        action = Action.UP
                else:
                    last_two_percepts = self.knowledge["percepts"][-2:]
                    # If can still go up, go up
                    if (
                        last_two_percepts[0]["pos"][1] < last_two_percepts[1]["pos"][1]
                        and self.action_temp == Action.UP
                    ):
                        action = Action.UP
                    else:
                        # If can't go up, drop.
                        # But before dropping, check if there already is a waste on the cell.
                        if last_percept["waste_on_pos"] is None:
                            action = Action.DROP
                        else:
                            # if there is a waste, and the wastes are the same color, pick and merge them
                            if (
                                last_percept["wastes"][0].indicate_color()
                                == last_percept["waste_on_pos"]
                            ):
                                action = Action.TAKE
                            else:
                                # Otherwise, go somewhere else to drop it
                                movables = [Action.LEFT, Action.RIGHT]
                                action = movables[self.random.randrange(len(movables))]
            elif len(self.knowledge["percepts"]) == 1:
                action = Action.UP

        return action
