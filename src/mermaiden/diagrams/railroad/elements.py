
from ...core.element import Container, Entity, RequiresChildren


class Terminal(Entity):
    pass


class NonTerminal(Entity):
    pass


class Special(Entity):
    pass


class CompositeExpression(Container, RequiresChildren):
    pass


class SequenceExpression(CompositeExpression):
    pass


class AlternativeExpression(CompositeExpression):
    pass


class OptionalExpression(CompositeExpression):
    pass


class RepetitionExpression(CompositeExpression):
    pass


class GroupExpression(CompositeExpression):
    pass
