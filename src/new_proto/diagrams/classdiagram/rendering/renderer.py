from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..diagram import ClassDiagram


@injectable(as_type=DiagramMmdRenderer, qualifier="classdiagram")
@dataclass(frozen=True, slots=True)
class ClassDiagramMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = ClassDiagram
    template_package: ClassVar[str] = "new_proto.diagrams.classdiagram.rendering"
    template_namespace: ClassVar[str] = "classdiagram"
