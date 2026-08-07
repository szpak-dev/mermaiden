from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from wireup import injectable

from ...core.annotation import TargetKind, TargetRef
from ...core.constraint import ChangeReport
from ..base import DomainDiagram
from .annotations import TreeAnnotation
from .changes import TreeViewChanges
from .elements import TreeItem
from .observer import TreeViewObserver
from .relations import TreeBranch
from .runtime import TreeViewAnnotations, TreeViewElements, TreeViewRelations, TreeViewState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeView(DomainDiagram):
    state: TreeViewState
    elements: TreeViewElements
    relations: TreeViewRelations
    annotations: TreeViewAnnotations
    changes: TreeViewChanges
    observer: TreeViewObserver

    @property
    def kind(self) -> str:
        return "treeView-beta"

    def add_container(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_item(id, label, parent_id)

    def add_entity(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_item(id, label, parent_id)

    def add_item(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add tree item '{id}'", TreeItem(id, label), parent_id)

    def connect(self, id: str, element_ids: Sequence[str], label: str = "") -> ChangeReport:
        return self._add_relation(f"add tree branch '{id}'", TreeBranch(id, tuple(element_ids), label))

    def add_branch(self, id: str, parent_id: str, child_id: str) -> ChangeReport:
        return self.connect(id, (parent_id, child_id))

    def annotate(
        self,
        id: str,
        data: Mapping[str, object],
        element_ids: Sequence[str] = (),
        relation_ids: Sequence[str] = (),
    ) -> ChangeReport:
        operation = f"add tree annotation '{id}'"
        if relation_ids or len(element_ids) != 1:
            self.changes.reject(operation, "Tree View annotations target exactly one element.")
        allowed = {"highlight", "icon", "description"}
        if not data or not set(data).issubset(allowed):
            self.changes.reject(operation, "Tree View annotations use highlight, icon, and/or description.")
        highlight = data.get("highlight", False)
        icon = data.get("icon", "")
        description = data.get("description", "")
        if not isinstance(highlight, bool) or not isinstance(icon, str) or not isinstance(description, str):
            self.changes.reject(operation, "Tree View annotation values must be bool or strings.")
        if "\n" in description or "\r" in description:
            self.changes.reject(operation, "Tree View descriptions must be one line.")
        target = TargetRef(TargetKind.ELEMENT, element_ids[0])
        return self._add_annotation(operation, TreeAnnotation(id, (target,), highlight, icon, description))

    def add_annotation(
        self,
        id: str,
        element_id: str,
        *,
        highlight: bool = False,
        icon: str = "",
        description: str = "",
    ) -> ChangeReport:
        return self.annotate(
            id,
            {"highlight": highlight, "icon": icon, "description": description},
            element_ids=(element_id,),
        )
