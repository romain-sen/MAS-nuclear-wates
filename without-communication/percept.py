from typing import TypedDict, Tuple


class Percept(TypedDict):
    radiactivity: float
    waste1: str
    waste2: str
    pos: Tuple[int, int]
    other_on_pos: bool
