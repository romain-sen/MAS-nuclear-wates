from mesa import Agent

from action import Action
from types_1 import AgentColor, Knowledge, Percept, NuclearWasteModel


def update(knowledge: Knowledge, percepts: Percept, actions: Action):
    if percepts:
        knowledge["percepts"].append(percepts)
    if actions:
        knowledge["actions"].append(actions)


class CleaningAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model: NuclearWasteModel):
        super().__init__(unique_id, model)
        self.color = color
        self.knowledge = {"actions": [], "percepts": []}
        self.percept_temp = Percept(
            radiactivity=0,
            waste1=None,
            waste2=None,
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


class RandomCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        # Choose randomly an action to move
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        return movables[self.random.randrange(4)]


class DefaultAgent(CleaningAgent):
    def deliberate(self) -> Action:
        last_percept = self.give_last_percept()
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        action = movables[self.random.randrange(4)]
        # If the agent is on a waste, not on the top row and has a free spot, take it
        if (
            (last_percept["waste1"] is None or last_percept["waste2"] is None)
            and self.model.is_on_waste(self.pos) is not None
            and last_percept["pos"][1] < self.model.height - 1
        ):
            # TODO : Check if the agent is on top without using the height of the grid
            action = Action.TAKE

        # If the agent has a waste, go up to drop it on the top row
        if last_percept["waste1"] is not None:
            if len(self.knowledge["percepts"]) > 1:
                # Try to go up first
                if self.action_temp != Action.UP:
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
                        action = Action.DROP
            elif len(self.knowledge["percepts"]) == 1:
                action = Action.UP

        return action
