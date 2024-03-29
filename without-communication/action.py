import enum


class Action(enum.Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3
    TAKE = 4
    DROP = 5
    MERGE = 6

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


def move_agent(agent, action):
    if action == Action.LEFT:
        pass
    elif action == Action.RIGHT:
        pass
    elif action == Action.UP:
        pass
    elif action == Action.DOWN:
        pass
    else:
        raise ValueError("Unknown action: {}".format(action))


def take(agent):
    pass


def drop(agent):
    pass


def merge(agent):
    pass


def get_action_handler(action):
    """Maps each action to its corresponding handler."""
    action_mapping = {
        Action.LEFT: (lambda agent, environment: move_agent(agent, Action.LEFT)),
        Action.RIGHT: (lambda agent, environment: move_agent(agent, Action.RIGHT)),
        Action.UP: (lambda agent, environment: move_agent(agent, Action.UP)),
        Action.DOWN: (lambda agent, environment: move_agent(agent, Action.DOWN)),
        Action.TAKE: take,
        Action.DROP: drop,
        Action.MERGE: merge,
    }

    handler = action_mapping.get(action, None)
    if handler is None:
        raise NotImplementedError(f"No handler implemented for {action}")
    return handler


def handle_action(agent, action, environment):
    """Executes the corresponding handler based on the action."""
    action_enum = Action(action)
    handler = get_action_handler(action_enum)
    return handler(agent, environment)
