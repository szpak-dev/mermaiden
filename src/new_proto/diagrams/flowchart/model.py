from ...core.annotation import Annotation
from ...core.constraint import Constraint
from .diagram import Flow, FlowNode, FlowNodeGroup, FlowchartDiagram
from .elements import Start


class StartElement(Start):
    def __init__(self, id: str):
        self._id = id

    @property
    def id(self) -> str:
        return self._id


class Flowchart(FlowchartDiagram):
    def __init__(
        self,
        elements: tuple[FlowNode | FlowNodeGroup, ...],
        relations: tuple[Flow, ...] = (),
        annotations: tuple[Annotation, ...] = (),
        constraints: tuple[Constraint, ...] = (),
    ):
        self._elements = elements
        self._relations = relations
        self._annotations = annotations
        self._constraints = constraints

    @property
    def elements(self) -> tuple[FlowNode | FlowNodeGroup, ...]:
        return self._elements

    @property
    def relations(self) -> tuple[Flow, ...]:
        return self._relations

    @property
    def annotations(self) -> tuple[Annotation, ...]:
        return self._annotations

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        return self._constraints
