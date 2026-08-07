from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DefinedDiagram, DiagramDefinition
from .annotations import Notes
from .changes import FlowchartChanges
from .elements import (
    Action,
    DataStore,
    Decision,
    Direction,
    Document,
    End,
    FlowGroup,
    FlowNode,
    InputOutput,
    Junction,
    Start,
    Subprocess,
)
from .observer import FlowchartObserver
from .relations import ConditionalFlow, Flow
from .runtime import FlowchartAnnotations, FlowchartElements, FlowchartRelations, FlowchartState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Flowchart(DefinedDiagram):
    state: FlowchartState
    elements: FlowchartElements
    relations: FlowchartRelations
    annotations: FlowchartAnnotations
    changes: FlowchartChanges
    observer: FlowchartObserver
    direction: Direction = Direction.TOP_DOWN

    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        kind="flowchart",
        entity_name="node",
        container_name="flow group",
        relation_name="flow",
        annotation_name="note",
        entity=FlowNode,
        container=FlowGroup,
        relation=Flow,
        annotation=Notes(),
    )

    @property
    def mmd_header(self) -> str:
        return f"{self.kind} {self.direction.value}"

    def add_group(
        self,
        id: str,
        label: str,
        parent_id: str = "",
        direction: Direction | None = None,
    ) -> ChangeReport:
        return self._add_element(
            f"add flow group '{id}'",
            FlowGroup(id, label, (), direction),
            parent_id,
        )

    def add_node(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_entity(id, label, parent_id)

    def add_start(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Start(id, label), parent_id, "start")

    def add_end(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(End(id, label), parent_id, "end")

    def add_action(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Action(id, label), parent_id, "action")

    def add_decision(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Decision(id, label), parent_id, "decision")

    def add_input_output(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(InputOutput(id, label), parent_id, "input/output")

    def add_data_store(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(DataStore(id, label), parent_id, "data store")

    def add_document(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Document(id, label), parent_id, "document")

    def add_subprocess(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Subprocess(id, label), parent_id, "subprocess")

    def add_junction(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_node(Junction(id, label), parent_id, "junction")

    def add_flow(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str = "",
    ) -> ChangeReport:
        return self.connect(id, (source_id, target_id), label)

    def add_conditional_flow(
        self,
        id: str,
        source_id: str,
        target_id: str,
        condition: str,
    ) -> ChangeReport:
        return self._add_relation(
            f"add conditional flow '{id}'",
            ConditionalFlow(id, (source_id, target_id), condition),
        )

    def add_note(
        self,
        id: str,
        text: str,
        element_ids: Sequence[str] = (),
    ) -> ChangeReport:
        return self.annotate(
            id,
            {"text": text},
            element_ids=element_ids,
        )

    def remove_flow(self, id: str) -> ChangeReport:
        return self.remove_relation(id)

    def _add_node(self, node: FlowNode, parent_id: str, kind: str) -> ChangeReport:
        return self._add_element(f"add {kind} '{node.id}'", node, parent_id)
