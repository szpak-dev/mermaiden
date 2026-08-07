from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar

from wireup import injectable

from ...core.constraint import ChangeReport
from ..domain import DiagramDefinition, DiagramMembers, DiagramModel
from .annotations import TreeAnnotations, TreeViewAnnotationMember
from .configuration import TreeViewDiagramConfiguration
from .constraints import TreeViewConstraint
from .elements import TreeItem, TreeViewElementMember
from .relations import TreeBranch, TreeViewRelationMember


@injectable(as_type=DiagramModel, qualifier="treeview", lifetime="scoped")
@dataclass(frozen=True, slots=True)
class TreeView(DiagramModel):
    constraints: Sequence[TreeViewConstraint]
    members: ClassVar[DiagramMembers] = DiagramMembers(
        "treeview.members",
        TreeViewElementMember,
        TreeViewRelationMember,
        TreeViewAnnotationMember,
    )
    configuration: TreeViewDiagramConfiguration = field(default_factory=TreeViewDiagramConfiguration, init=False)
    definition: ClassVar[DiagramDefinition] = DiagramDefinition(
        "treeView-beta",
        "Tree view",
        "treeView",
        "TreeViewDiagramConfig",
    )


    @property
    def root_elements(self) -> tuple[TreeItem, ...]:
        child_ids = {
            relation.child_id
            for relation in self.find_relations()
            if isinstance(relation, TreeBranch) and len(relation.element_ids) == 2
        }
        return tuple(item for item in super().root_elements if isinstance(item, TreeItem) and item.id not in child_ids)

    def add_item(self, id: str, label: str, parent_id: str = "") -> ChangeReport:
        return self._add_element(f"add tree item '{id}'", TreeItem(id, label), parent_id)

    def add_branch(self, id: str, parent_id: str, child_id: str) -> ChangeReport:
        return self._add_relation(f"add tree branch '{id}'", TreeBranch(id, (parent_id, child_id)))

    def add_annotation(
        self,
        id: str,
        element_id: str,
        *,
        highlight: bool = False,
        icon: str = "",
        description: str = "",
    ) -> ChangeReport:
        return self._annotate(
            f"add tree annotation '{id}'",
            TreeAnnotations(),
            id,
            {"highlight": highlight, "icon": icon, "description": description},
            (element_id,),
        )
