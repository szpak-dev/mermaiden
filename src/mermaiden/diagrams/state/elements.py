
from ...core.element import Container, Entity


class StateEndpoint:
    pass


class StateNode(Entity, StateEndpoint):
    pass


class State(StateNode):
    pass


class Initial(StateNode):
    pass


class Final(StateNode):
    pass


class Choice(StateNode):
    pass


class Fork(StateNode):
    pass


class Join(StateNode):
    pass


class CompositeState(Container, StateEndpoint):
    pass
