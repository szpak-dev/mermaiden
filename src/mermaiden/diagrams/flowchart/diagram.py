from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramModel
from .annotations import Notes
from .configuration import FlowchartDiagramConfiguration
from .constraints.constraint import FlowchartConstraint
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
from .relations import ConditionalFlow, Flow


@injectable(as_type=DiagramModel, qualifier="flowchart", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Flowchart(DiagramModel):
    constraints: Sequence[FlowchartConstraint]
    configuration: FlowchartDiagramConfiguration = field(default_factory=FlowchartDiagramConfiguration, init=False)
    direction: Direction = field(default=Direction.TOP_DOWN, init=False)
    syntax: ClassVar[str] = "flowchart"
    name: ClassVar[str] = "Flowchart"
    config_key: ClassVar[str] = "flowchart"
    schema_definition: ClassVar[str] = "FlowchartDiagramConfig"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return self.configuration.document(self.config_key).to_mermaid()

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
        return self._add_node(FlowNode(id, label), parent_id, "node")

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
        return self._add_relation(f"add flow '{id}'", Flow(id, (source_id, target_id), label))

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
        return self._annotate(
            f"add note '{id}'",
            Notes(),
            id,
            {"text": text},
            element_ids,
        )

    def remove_flow(self, id: str) -> ChangeReport:
        return self.remove_relation(id)

    def _add_node(self, node: FlowNode, parent_id: str, kind: str) -> ChangeReport:
        return self._add_element(f"add {kind} '{node.id}'", node, parent_id)
