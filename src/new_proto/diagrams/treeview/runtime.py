from dataclasses import dataclass

from wireup import injectable

from ...runtime.diagrams.annotations import Annotations
from ...runtime.diagrams.elements import Elements
from ...runtime.diagrams.relations import Relations
from ...runtime.diagrams.state import DiagramState
from ...runtime.diagrams.transaction import ChangeTransaction


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewState(DiagramState):
    pass


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewElements(Elements):
    state: TreeViewState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewRelations(Relations):
    state: TreeViewState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewAnnotations(Annotations):
    state: TreeViewState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeViewTransaction(ChangeTransaction):
    state: TreeViewState
