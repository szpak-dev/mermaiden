from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from ..flowchart.elements import Direction
from .annotations import NotePosition, StateNote, StateNotes
from .configuration import StateDiagramConfiguration
from .constraints.constraint import StateDiagramConstraint
from .elements import Choice, CompositeState, Final, Fork, Initial, Join, State, StateNode
from .relations import StateTransition


@injectable(as_type=DiagramModel, qualifier="state", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class StateDiagram(DiagramModel):
    constraints: Sequence[StateDiagramConstraint]
    configuration: StateDiagramConfiguration = field(default_factory=StateDiagramConfiguration, init=False)
    direction: Direction = field(default=Direction.TOP_DOWN, init=False)
    syntax: ClassVar[str] = "stateDiagram-v2"
    name: ClassVar[str] = "State diagram"
    config_key: ClassVar[str] = "state"
    schema_definition: ClassVar[str] = "StateDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {self.config_key: self.configuration.to_mermaid()}

    def add_state(self, id: str, label: str = "", composite_id: str = "") -> ChangeReport:
        return self._add_node(State(id, label), composite_id, "state")

    def add_initial(self, id: str, composite_id: str = "") -> ChangeReport:
        return self._add_node(Initial(id, "initial"), composite_id, "initial state")

    def add_final(self, id: str, composite_id: str = "") -> ChangeReport:
        return self._add_node(Final(id, "final"), composite_id, "final state")

    def add_composite(self, id: str, label: str = "", composite_id: str = "") -> ChangeReport:
        return self._add_node(CompositeState(id, label), composite_id, "composite state")

    def add_choice(self, id: str, label: str = "", composite_id: str = "") -> ChangeReport:
        return self._add_node(Choice(id, label), composite_id, "choice")

    def add_fork(self, id: str, label: str = "", composite_id: str = "") -> ChangeReport:
        return self._add_node(Fork(id, label), composite_id, "fork")

    def add_join(self, id: str, label: str = "", composite_id: str = "") -> ChangeReport:
        return self._add_node(Join(id, label), composite_id, "join")

    def add_transition(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str = "",
        composite_id: str = "",
    ) -> ChangeReport:
        return self._add_relation(
            f"add transition '{id}'",
            StateTransition(
                id,
                (source_id, target_id),
                label,
                composite_id,
                isinstance(self.find_element(source_id), Initial),
                isinstance(self.find_element(target_id), Final),
            ),
        )

    def add_note(
        self,
        id: str,
        state_id: str,
        text: str,
        position: NotePosition = NotePosition.RIGHT,
        composite_id: str = "",
    ) -> ChangeReport:
        return self._annotate(
            f"add note '{id}'",
            StateNotes(),
            id,
            {"text": text, "position": position, "scope_id": composite_id},
            (state_id,),
        )

    def transitions_for(self, composite_id: str = "") -> tuple[StateTransition, ...]:
        return tuple(
            item
            for item in self.find_relations()
            if isinstance(item, StateTransition) and item.scope_id == composite_id
        )

    def notes_for(self, composite_id: str = "") -> tuple[StateNote, ...]:
        return tuple(
            item
            for item in self.find_annotations()
            if isinstance(item, StateNote) and item.scope_id == composite_id
        )

    def remove_transition(self, id: str) -> ChangeReport:
        return self.remove_relation(id)

    def _add_node(self, node: StateNode | CompositeState, composite_id: str, kind: str) -> ChangeReport:
        return self._add_element(f"add {kind} '{node.id}'", node, composite_id)
