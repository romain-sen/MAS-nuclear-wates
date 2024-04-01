from typing import Dict, List, TypedDict
import enum

from mesa import Agent

from action import Action
from percept import Percept


class Knowledge(TypedDict):
    actions: List[Action]
    percepts: List[Percept]


class AgentColor(enum.Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


knowledges: Knowledge = {
    "actions": [
        Action.STAY,
        Action.RIGHT,
    ],
    "percepts": [
        {
            "radiactivity": 0.11,
            "waste1": "green",
            "waste2": "empty",
            "pos": (1, 2),
            "other_on_pos": True,
        },
        {
            "radiactivity": 0.23,
            "waste1": "green",
            "waste2": "green",
            "pos": (2, 2),
            "other_on_pos": False,
        },
    ],
}


def update(knowledge: Knowledge, percepts: Percept, actions: Action):
    knowledge["percepts"].extend(percepts)
    knowledge["actions"].extend(actions)


class CleaningAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model):
        super().__init__(unique_id, model)
        self.color = color
        self.knowledge = knowledges
        self.percept_temp = None
        self.action_temp = None

    def deliberate(self) -> Action:
        pass

    def step(self):
        update(self.knowledge, self.percept_temp, self.action_temp)
        action = self.deliberate()
        self.action_temp = action
        self.percept_temp = self.model.do(self, action)


class ExampleCleaningAgent(CleaningAgent):
    def deliberate(self) -> Action:
        # Choose randomly an action to move
        movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
        return movables[self.random.randrange(4)]
