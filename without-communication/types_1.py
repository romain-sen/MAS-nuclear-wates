import enum
from typing import Dict, List, TypedDict, Tuple
from mesa import Agent, Model


class Percept(TypedDict):
    radiactivity: float
    waste1: str
    waste2: str
    pos: Tuple[int, int]
    other_on_pos: bool


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


class Knowledge(TypedDict):
    actions: List[Action]
    percepts: List[Percept]


class AgentColor(enum.Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


class PickedWastes:
    def __init__(self, agentId: int, wasteId: int, wasteColor: AgentColor):
        self.agentId = agentId
        self.wasteId = wasteId
        self.wasteColor = wasteColor


class CleaningAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model): ...

    def deliberate(self) -> Action: ...

    def step(self): ...


class RadioactivityAgent(Agent):
    def __init__(self, unique_id, radioactivity, model): ...

    def step(self): ...

    def indicate_radioactivity(self): ...


class WasteAgent(Agent):
    def __init__(self, unique_id: int, radioactivity: float, model): ...

    def step(self): ...

    def indicate_radioactivity(self) -> float: ...


class NuclearWasteModel(Model):
    """
    The environment of the model.
    """

    def __init__(self, N_AGENTS, N_WASTES, width, height): ...

    def step(self): ...

    def perceive(self, agent): ...

    def do(self, agent, action): ...

    def others_on_pos(self, agent: CleaningAgent): ...

    def get_radioactivity(self, pos): ...

    def get_who_picked_waste(self, waste_id: int) -> int | None: ...

    def give_waste_agent(self, waste_id: int, waste_color, agent_id: int): ...

    def drop_waste(self, waste_id: int, agent_id: int, pos: tuple[int, int]): ...

    def merge_wastes(
        self, waste_id1: int, waste_id2: int, agent_id: int
    ) -> WasteAgent | None: ...
