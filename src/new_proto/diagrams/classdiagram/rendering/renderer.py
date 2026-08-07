from dataclasses import dataclass
from typing import ClassVar

from jinja2 import PackageLoader
from wireup import injectable

from ....core.diagram import DiagramView
from ....rendering.jinja import JinjaTextRenderer, create_jinja_environment
from ...rendering import DiagramMmdRenderer
from ..diagram import ClassDiagram


@dataclass(frozen=True, slots=True)
class ClassDiagramMmdRenderer(DiagramMmdRenderer):
    template: JinjaTextRenderer[ClassDiagram]
    diagram_type: ClassVar[type[DiagramView]] = ClassDiagram

    def _render(self, diagram: DiagramView) -> str:
        assert isinstance(diagram, ClassDiagram)
        return self.template.render(diagram)


@injectable(as_type=DiagramMmdRenderer, qualifier="classdiagram")
def create_classdiagram_mmd_renderer() -> ClassDiagramMmdRenderer:
    environment = create_jinja_environment(PackageLoader("new_proto.diagrams.classdiagram.rendering", "templates"))
    return ClassDiagramMmdRenderer(JinjaTextRenderer[ClassDiagram](environment, "diagram.mmd.j2"))

