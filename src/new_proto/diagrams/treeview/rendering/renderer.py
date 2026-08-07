from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..annotations import TreeAnnotation
from ..diagram import TreeView
from ..elements import TreeItem
from ..relations import TreeBranch
from .syntax import tree_label


@dataclass(frozen=True, slots=True)
class TreeViewRenderModel:
    roots: Sequence[TreeItem]
    children: Mapping[str, Sequence[TreeItem]]
    annotations: Mapping[str, Sequence[TreeAnnotation]]


@injectable(as_type=DiagramMmdRenderer, qualifier="treeview")
@dataclass(frozen=True, slots=True)
class TreeViewMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = TreeView
    template_package: ClassVar[str] = "new_proto.diagrams.treeview.rendering"
    template_filters: ClassVar = {"tree_label": tree_label}

    def model(self, diagram: DiagramView) -> TreeViewRenderModel:
        assert isinstance(diagram, TreeView)
        return self._model(diagram)

    @staticmethod
    def _model(diagram: TreeView) -> TreeViewRenderModel:
        elements = tuple(item for item in diagram.walk_elements() if isinstance(item, TreeItem))
        items = {item.id: item for item in elements}
        children: dict[str, list[TreeItem]] = defaultdict(list)
        child_ids: set[str] = set()
        for relation in diagram.find_relations():
            if isinstance(relation, TreeBranch) and len(relation.element_ids) == 2:
                child = items.get(relation.child_id)
                if child is not None:
                    children[relation.parent_id].append(child)
                    child_ids.add(child.id)
        annotations: dict[str, list[TreeAnnotation]] = defaultdict(list)
        for annotation in diagram.find_annotations():
            if isinstance(annotation, TreeAnnotation) and annotation.targets:
                annotations[annotation.targets[0].id].append(annotation)
        return TreeViewRenderModel(
            roots=tuple(item for item in elements if item.id not in child_ids),
            children={item.id: tuple(children[item.id]) for item in elements},
            annotations={item.id: tuple(annotations[item.id]) for item in elements},
        )
