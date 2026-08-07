from dataclasses import dataclass
from typing import ClassVar

from jinja2 import PackageLoader
from wireup import injectable

from ....core.diagram import DiagramView
from ....rendering.jinja import JinjaTextRenderer, create_jinja_environment
from ...rendering import DiagramMmdRenderer
from ..diagram import Flowchart
from .syntax import mermaid_identifier, mermaid_quote


@dataclass(frozen=True, slots=True)
class FlowchartMmdRenderer(DiagramMmdRenderer):
    template: JinjaTextRenderer[Flowchart]

    diagram_type: ClassVar[type[DiagramView]] = Flowchart

    def _render(self, diagram: DiagramView) -> str:
        assert isinstance(diagram, Flowchart)
        return self.template.render(diagram)


@injectable(as_type=DiagramMmdRenderer, qualifier="flowchart")
def create_flowchart_mmd_renderer() -> FlowchartMmdRenderer:
    environment = create_jinja_environment(
        PackageLoader("new_proto.diagrams.flowchart.rendering", "templates"),
        filters={
            "mmd_id": mermaid_identifier,
            "mmd_quote": mermaid_quote,
        },
    )
    template = JinjaTextRenderer[Flowchart](environment, "diagram.mmd.j2")
    return FlowchartMmdRenderer(template)


__all__ = ["FlowchartMmdRenderer"]
