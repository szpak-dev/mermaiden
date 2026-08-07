from dataclasses import dataclass

from jinja2 import PackageLoader
from wireup import injectable

from ....core.diagram import DiagramView
from ....core.error import OperationError
from ....rendering.jinja import JinjaTextRenderer, create_jinja_environment
from ...rendering import DiagramMmdRenderer
from ..diagram import Flowchart
from .syntax import mermaid_identifier, mermaid_quote


@dataclass(frozen=True, slots=True)
class FlowchartMmdRenderer(DiagramMmdRenderer):
    template: JinjaTextRenderer[Flowchart]

    def render(self, diagram: Flowchart) -> str:
        return self.template.render(diagram)

    def can_render(self, diagram: DiagramView) -> bool:
        return isinstance(diagram, Flowchart)

    def render_body(self, diagram: DiagramView) -> str:
        if not self.can_render(diagram):
            raise OperationError(f"Flowchart renderer cannot render diagram kind '{diagram.kind}'.")
        assert isinstance(diagram, Flowchart)
        return self.render(diagram)


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
