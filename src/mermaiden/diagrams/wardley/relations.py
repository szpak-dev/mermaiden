from ...core.domain import Relation


class Dependency(Relation):
    operator: str = "->"
