from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..base import DefinedDiagram, DiagramDefinition
from .annotations import TreeAnnotations
from .changes import TreeViewChanges
from .elements import TreeItem
from .observer import TreeViewObserver
from .relations import TreeBranch
from .runtime import TreeViewAnnotations, TreeViewElements, TreeViewRelations, TreeViewState


@injectable(lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeView(DefinedDiagram):
    state: TreeViewState
    elements: TreeViewElements
    relations: TreeViewRelations
    annotations: TreeViewAnnotations
    changes: TreeViewChanges
    observer: TreeViewObserver

    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        kind="treeView-beta",
        entity_name="tree item",
        container_name="tree item",
        relation_name="tree branch",
        annotation_name="tree annotation",
        entity=TreeItem,
        container=TreeItem,
        relation=TreeBranch,
        annotation=TreeAnnotations(),
    )

    def add_item(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self.add_entity(id, label, parent_id)

    def add_branch(self, id: str, parent_id: str, child_id: str) -> ChangeReport:
        return self.connect(id, (parent_id, child_id))

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
