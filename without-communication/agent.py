from typing import Dict, List

from mesa import Agent

from action import Action
from percept import Percept


knowledges: Dict[str, List[Percept | Action]] = {
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


class MoneyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

    def receive(self, amount):
        self.wealth += amount
        # print(f"Agent {self.unique_id} has received {amount}")

    def share_with_neighbors(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            if self.wealth > 0:
                amount = 1
                self.wealth -= amount
                other.receive(amount)
                # print(f"Agent {self.unique_id} has given {amount} to Agent {other.unique_id}")

    def move(self):
        self.model.grid.move_agent(
            self,
            self.random.choice(self.model.grid.get_neighborhood(self.pos, moore=True)),
        )

    def step(self):
        self.move()
        self.share_with_neighbors()

    def indicate_wealth(self):
        return self.wealth
