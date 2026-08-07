from typing import ClassVar

from wireup import injectable

from ...domain import DiagramMembersConstraint
from ..annotations import StateNote
from ..elements import CompositeState, StateNode
from ..relations import StateTransition
from .constraint import StateDiagramConstraint


@injectable(as_type=StateDiagramConstraint, qualifier="state_members")
class StateContainsOnlyStateMembers(DiagramMembersConstraint, StateDiagramConstraint):
    element_types: ClassVar = (StateNode, CompositeState)
    relation_types: ClassVar = (StateTransition,)
    annotation_types: ClassVar = (StateNote,)
    element_description: ClassVar[str] = "valid in a state diagram"
    relation_description: ClassVar[str] = "a state transition"
    annotation_description: ClassVar[str] = "a state note"

    @property
    def code(self) -> str:
        return "state.member_type"
