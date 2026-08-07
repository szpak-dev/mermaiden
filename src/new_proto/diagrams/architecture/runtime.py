from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.annotations import Annotations
from ...runtime.diagrams.elements import Elements
from ...runtime.diagrams.relations import Relations
from ...runtime.diagrams.state import DiagramState
from ...runtime.diagrams.transaction import ChangeTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureState(DiagramState):
    pass


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureElements(Elements):
    state: ArchitectureState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureRelations(Relations):
    state: ArchitectureState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureAnnotations(Annotations):
    state: ArchitectureState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class ArchitectureTransaction(ChangeTransaction):
    state: ArchitectureState
