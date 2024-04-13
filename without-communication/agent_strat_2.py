from action import Action
from agent import CleaningAgent
from types_1 import AgentColor, DEPOSIT_RADIOACTIVITY, NeighboringType


class MergerAgent(CleaningAgent):
    """
    Takes care of merging wastes.
    """
    def deliberate(self) -> Action:
        last_percept = self.give_last_percept()

        # If the agent can merge wastes, merge them
        if (
            len(last_percept["wastes"]) == 2
            and last_percept["wastes"][0].indicate_color()
            == last_percept["wastes"][1].indicate_color()
        ):  
            print("merge !")
            return Action.MERGE
        
        # If the agent is on a waste, take it if possible
        elif self.model.is_on_waste(self.pos) is not None:
            if len(last_percept["wastes"]) == 0:
                return Action.TAKE
                print("take !")
            elif (
                len(last_percept["wastes"]) == 1 
                and last_percept["wastes"][0].indicate_color() == self.model.is_on_waste(self.pos)
            ):
                print("take !")
                return Action.TAKE
                
        # If the agent has a transformed waste, take it to the east or drop it if already at the border
        elif (
            (self.color == AgentColor.GREEN
            and len(last_percept["wastes"]) == 1
            and last_percept["wastes"][0].indicate_color() == AgentColor.YELLOW)
            or (self.color == AgentColor.YELLOW
            and len(last_percept["wastes"]) == 1
            and last_percept["wastes"][0].indicate_color() == AgentColor.RED)
        ):
            if self.pos[0] != self.knowledge["x_max"]:
                print("go right !")
                return Action.RIGHT
            else:
                print("drop !")
                return Action.DROP
        
        # If red robot and has a red waste, take it to disposal zone
        elif (
            self.color == AgentColor.RED
            and len(last_percept["wastes"]) == 1 
            and last_percept["wastes"][0].indicate_color() == AgentColor.RED
        ):
            if last_percept["radiactivity"] == DEPOSIT_RADIOACTIVITY:
                print("drop at deposit !")
                return Action.DROP
            elif self.pos[0] != self.knowledge["grid_width"]:
                print("go right !")
                return Action.RIGHT
            else:
                print("go up !")
                return Action.UP
            
        # Check surrounding cells and take appropriate action
        else:
            wastes = [(type, agentColor, pos) for (type, agentColor, pos) in last_percept["surrounding"] if type == NeighboringType.WASTE]
            print("wastes", wastes)
            print("surrounding", last_percept["surrounding"])
            if len(wastes) != 0:
                if wastes[0][0] < self.pos[0]:
                    print("left to get waste !")
                    return Action.LEFT
                elif wastes[0][0] > self.pos[0]:
                    print("right to get waste !")
                    return Action.RIGHT
                elif wastes[0][1] < self.pos[1]:
                    print("down to get waste !")
                    return Action.DOWN
                elif wastes[0][1] > self.pos[1]:
                    print("up to get waste !")
                    return Action.UP
            
            else:
                movables = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
                print("random move !")
                return movables[self.random.randrange(len(movables))]


def add_merger_agents(environment, num_agents: int, agent_color: AgentColor):
    """
    Adds merger agents to the environment.

    :param environment: The environment where agents are added.
    :param num_agents: The number of agents to add.
    :param agent_color: The specific color for all agents; if None, assigns random colors.
    """
    for i in range(num_agents):
        environment.obj_id += 1

        # Set movement boundaries based on the agent's color.
        if agent_color == AgentColor.RED:
            x = environment.random.randrange(
                2 * environment.grid.width // 3, environment.grid.width
            )
        elif agent_color == AgentColor.YELLOW:
            x = environment.random.randrange(
                environment.grid.width // 3, 2 * environment.grid.width // 3
            )
        else:  # AgentColor.GREEN
            x = environment.random.randrange(0, environment.grid.width // 3)

        y = environment.random.randrange(environment.grid.height)

        # Create and add the agent to the environment.
        agent = MergerAgent(
            unique_id=environment.obj_id, color=agent_color, x_max=x, model=environment
        )
        environment.schedule.add(agent)
        environment.grid.place_agent(agent, (x, y))

def add_agents_strat_2(environment, n_green_agents, n_yellow_agents, n_red_agents):
    """
    Add agents to the environment.
    """
    add_merger_agents(environment, n_green_agents, AgentColor.GREEN)
    add_merger_agents(environment, n_yellow_agents, AgentColor.YELLOW)
    add_merger_agents(environment, n_red_agents, AgentColor.RED)
    