from ...core.domain import Container, Entity


class Terminal(Entity):
    pass


class NonTerminal(Entity):
    pass


class Special(Entity):
    pass


class CompositeExpression(Container):
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
