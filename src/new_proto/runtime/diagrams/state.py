from dataclasses import dataclass, field

from wireup import injectable

from ...core.annotation import Annotation
from ...core.element import Element
from ...core.error import OperationError
from ...core.relation import Relation


@dataclass(frozen=True, slots=True)
class DiagramData:
    elements: tuple[Element, ...] = ()
    relations: tuple[Relation, ...] = ()
    annotations: tuple[Annotation, ...] = ()


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class DiagramState:
    _committed: list[DiagramData] = field(default_factory=lambda: [DiagramData()], init=False)
    _candidate: list[DiagramData] = field(default_factory=lambda: list[DiagramData](), init=False)

    @property
    def current(self) -> DiagramData:
        return self._candidate[-1] if self._candidate else self._committed[-1]

    def stage(self, candidate: DiagramData) -> None:
        if self._candidate:
            raise OperationError("A diagram change is already in progress.")
        self._candidate.append(candidate)

    def commit(self) -> None:
        self._committed[0] = self._candidate.pop()

    def rollback(self) -> None:
        self._candidate.clear()
