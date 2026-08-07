from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from jinja2 import PackageLoader
from wireup import injectable

from ....core.diagram import DiagramView
from ....core.error import OperationError
from ....rendering.jinja import JinjaTextRenderer, create_jinja_environment
from ...rendering import DiagramMmdRenderer
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


@dataclass(frozen=True, slots=True)
class TreeViewMmdRenderer(DiagramMmdRenderer):
    template: JinjaTextRenderer[TreeViewRenderModel]

    def render(self, diagram: TreeView) -> str:
        return self.template.render(self._model(diagram))

    def can_render(self, diagram: DiagramView) -> bool:
        return isinstance(diagram, TreeView)

    def render_body(self, diagram: DiagramView) -> str:
        if not self.can_render(diagram):
            raise OperationError(f"Tree View renderer cannot render diagram kind '{diagram.kind}'.")
        assert isinstance(diagram, TreeView)
        return self.render(diagram)

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


@injectable(as_type=DiagramMmdRenderer, qualifier="treeview")
def create_treeview_mmd_renderer() -> TreeViewMmdRenderer:
    environment = create_jinja_environment(
        PackageLoader("new_proto.diagrams.treeview.rendering", "templates"),
        filters={"tree_label": tree_label},
    )
    return TreeViewMmdRenderer(JinjaTextRenderer[TreeViewRenderModel](environment, "diagram.mmd.j2"))


__all__ = ["TreeViewMmdRenderer"]
