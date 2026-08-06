from ...core.relation import Association
from ...runtime.relations import DirectedConnection
from .elements import FlowNode, Fork, Join


class Flow(DirectedConnection[FlowNode]):
    pass


class ConditionalFlow(Flow):
    def __init__(self, source: FlowNode, target: FlowNode, condition: str):
        super().__init__(source, target)
        self._condition = condition

    @property
    def condition(self) -> str:
        return self._condition


class ParallelRegion(Association):
    def __init__(self, fork: Fork, join: Join):
        self._fork = fork
        self._join = join

    @property
    def fork(self) -> Fork:
        return self._fork

    @property
    def join(self) -> Join:
        return self._join

    @property
    def participants(self) -> tuple[Fork | Join, Fork | Join]:
        return self._fork, self._join
