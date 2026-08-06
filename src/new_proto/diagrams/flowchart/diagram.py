from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.annotation import TargetKind, TargetRef
from ...core.constraint import ChangeReport
from ...core.error import OperationError
from ...runtime.diagrams.aggregate import DiagramAggregate
from .annotations import Note
from .changes import FlowchartChanges
from .elements import Action, Decision, Direction, End, FlowGroup, FlowNode, Start
from .observer import FlowchartObserver
from .relations import ConditionalFlow, Flow


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class Flowchart(DiagramAggregate):
    changes: FlowchartChanges
    observer: FlowchartObserver
    direction: Direction = Direction.TOP_DOWN

    @property
    def id(self) -> str:
        return "flowchart"

    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_group(id, label, parent_id)

    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_node(id, label, parent_id)

    def connect(
        self,
        id: str,
        element_ids: Sequence[str],
        label: str,
    ) -> ChangeReport:
        operation = f"add flow '{id}'"
        candidate = self.relations.add(Flow(id, tuple(element_ids), label))
        return self.changes.apply(operation, candidate, self)

    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        operation = f"add note '{id}'"
        targets = (
            *(TargetRef(TargetKind.ELEMENT, item) for item in element_ids),
            *(TargetRef(TargetKind.RELATION, item) for item in relation_ids),
        )
        candidate = self.annotations.add_annotation(Note(id, targets, dict(data)))
        return self.changes.apply(operation, candidate, self)

    def add_group(
        self,
        id: str,
        label: str,
        parent_id: str = "",
        direction: Direction | None = None,
    ) -> ChangeReport:
        operation = f"add flow group '{id}'"
        try:
            candidate = self.elements.add(FlowGroup(id, label, (), direction), parent_id)
        except OperationError as error:
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)

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

    def add_flow(
        self,
        id: str,
        source_id: str,
        target_id: str,
        label: str,
    ) -> ChangeReport:
        return self.connect(id, (source_id, target_id), label)

    def add_conditional_flow(
        self,
        id: str,
        source_id: str,
        target_id: str,
        condition: str,
        label: str,
    ) -> ChangeReport:
        operation = f"add conditional flow '{id}'"
        candidate = self.relations.add(
            ConditionalFlow(id, (source_id, target_id), label, condition)
        )
        return self.changes.apply(operation, candidate, self)

    def add_note(
        self,
        id: str,
        text: str,
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        return self.annotate(
            id,
            {"text": text},
            element_ids=element_ids,
            relation_ids=relation_ids,
        )

    def remove_flow(self, id: str) -> ChangeReport:
        return self.remove_relation(id)

    def _add_node(self, node: FlowNode, parent_id: str, kind: str) -> ChangeReport:
        operation = f"add {kind} '{node.id}'"
        try:
            candidate = self.elements.add(node, parent_id)
        except OperationError as error:
            self.changes.reject(operation, str(error))
        return self.changes.apply(operation, candidate, self)
