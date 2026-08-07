from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.annotations import Annotations
from ...runtime.diagrams.elements import Elements
from ...runtime.diagrams.relations import Relations
from ...runtime.diagrams.state import DiagramState
from ...runtime.diagrams.transaction import ChangeTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramState(DiagramState):
    pass


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramElements(Elements):
    state: ClassDiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramRelations(Relations):
    state: ClassDiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramAnnotations(Annotations):
    state: ClassDiagramState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ClassDiagramTransaction(ChangeTransaction):
    state: ClassDiagramState

