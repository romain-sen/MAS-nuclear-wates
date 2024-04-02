from mesa import Agent

from action import Action
from types_1 import AgentColor, Knowledge, Percept


def update(knowledge: Knowledge, percepts: Percept, actions: Action):
    if percepts:
        knowledge["percepts"].append(percepts)
    if actions:
        knowledge["actions"].append(actions)


class CleaningAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model):
        super().__init__(unique_id, model)
        self.color = color
        self.knowledge = {"actions": [], "percepts": []}
        self.percept_temp = None
        self.action_temp = None

    def deliberate(self) -> Action:
        pass

    def step(self):
        update(self.knowledge, self.percept_temp, self.action_temp)
        action = self.deliberate()
        self.action_temp = action
        self.percept_temp = self.model.do(self, action)

    def give_last_percept(self):
        return self.percept_temp


class RandomCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        # Choose randomly an action to move
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        return movables[self.random.randrange(4)]
