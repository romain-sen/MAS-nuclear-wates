import enum
from typing import Dict, List, TypedDict, Tuple, Optional
from mesa import Agent, Model


class AgentColor(enum.Enum):
    RED = 0
    YELLOW = 1
    GREEN = 2


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


class RadioactivityAgent(Agent):
    def __init__(self, unique_id, radioactivity, model): ...

    def step(self): ...

    def indicate_radioactivity(self): ...


class WasteAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model): ...

    def step(self): ...

    def indicate_color(self) -> AgentColor: ...

    def __str__(self) -> str:
        return f"WasteAgent(id={self.unique_id}, color={self.color}, pos={self.pos})"


class Percept(TypedDict):
    radiactivity: float
    wastes: List[WasteAgent]
    pos: Tuple[int, int]
    other_on_pos: bool
    waste_on_pos: Optional[AgentColor]

    def __str__(self) -> str:
        wastes_str = ", ".join([str(waste) for waste in self["wastes"]])
        return f"Percept(radiactivity={self['radiactivity']}, wastes=[{wastes_str}], pos={self['pos']}, other_on_pos={self['other_on_pos']}, waste_on_pos={self['waste_on_pos']})"


class Knowledge(TypedDict):
    actions: List[Action]
    percepts: List[Percept]
    grid_width: int
    grid_height: int


class PickedWastes:
    def __init__(self, agentId: int, wasteId: int, wasteColor: AgentColor):
        self.agentId = agentId
        self.wasteId = wasteId
        self.wasteColor = wasteColor

    def __str__(self) -> str:
        return f"PickedWastes(agentId={self.agentId}, wasteId={self.wasteId}, wasteColor={self.wasteColor})"


def find_picked_waste_by_id(
    waste_id: int, picked_wastes_list: List[PickedWastes]
) -> Optional[PickedWastes]: ...


class CleaningAgent(Agent):
    def __init__(self, unique_id: int, color: AgentColor, model): ...

    def deliberate(self) -> Action: ...

    def step(self): ...

    def give_last_percept(self) -> Percept: ...

    def indicate_color(self) -> AgentColor: ...


class RandomCleaningAgent(CleaningAgent): ...


class NuclearWasteModel(Model):
    """
    The environment of the model.
    """

    def __init__(self, N_AGENTS, N_WASTES, width, height): ...

    def step(self): ...

    def perceive(self, agent): ...

    def do(self, agent, action) -> Percept: ...

    def is_on_waste(self, pos) -> AgentColor: ...

    def others_on_pos(self, agent: CleaningAgent) -> bool: ...

    def get_radioactivity(self, pos): ...

    def get_who_picked_waste(self, waste_id: int) -> int: ...

    def give_waste_agent(
        self, waste_id: int, waste_color, agent_id: int, pos: tuple[int, int]
    ): ...

    def drop_waste(self, waste_id: int, pos: tuple[int, int]): ...

    def merge_wastes(
        self, waste_id1: int, waste_id2: int, agent_id: int, pos: tuple[int, int]
    ) -> WasteAgent: ...
