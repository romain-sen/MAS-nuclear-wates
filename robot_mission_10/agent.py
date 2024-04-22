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
            "last_pos": (0, 0),
            "have_saved_last_pos": False,
            "go_back": False,
        }
        self.percept_temp = Percept(
            radiactivity=0,
            wastes=[],
            pos=(0, 0),
            other_on_pos=False,
            waste_on_pos=None,
            surrounding=[],
        )
        self.action_temp = Action.STAY
        self.step_count = 0

    def deliberate(self) -> Action:
        pass

    def step(self):
        update(self.knowledge, self.percept_temp, self.action_temp)
        action = self.deliberate()
        self.action_temp = action
        self.percept_temp = self.model.do(self, action)
        if self.pos == self.knowledge["last_pos"]:
            self.knowledge["go_back"] = False
            self.knowledge["have_saved_last_pos"] = False
            self.knowledge["last_pos"] = self.pos

    def give_last_percept(self) -> Percept:
        return self.percept_temp

    def indicate_color(self):
        return self.color

    def __str__(self) -> str:
        return f"CleaningAgent(id={self.unique_id}, color={self.color}, pos={self.pos})"


def add_agents_template(environment, n_green_agents, n_yellow_agents, n_red_agents):
    """
    Function that add the agent to the environment.
    Must increase the obj_id of the environment at each agent added.

    Args:
        environment (NuclearWasteModel): The environment where agents are added.
        num_agents (int): The number of agents to add.
    """
    pass
