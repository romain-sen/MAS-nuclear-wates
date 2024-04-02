from typing import Dict, List, TypedDict, Tuple
import enum


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
