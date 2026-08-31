from ...core.domain import ConditionalRelation, Relation


class Flow(Relation):
    pass


class ConditionalFlow(Flow, ConditionalRelation):
    pass
