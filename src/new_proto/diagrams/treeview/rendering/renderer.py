from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..diagram import TreeView
from .syntax import tree_label


@injectable(as_type=DiagramMmdRenderer, qualifier="treeview")
@dataclass(frozen=True, slots=True)
class TreeViewMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = TreeView
    template_package: ClassVar[str] = "new_proto.diagrams.treeview.rendering"
    template_namespace: ClassVar[str] = "treeview"
    template_filters: ClassVar = {"tree_label": tree_label}
