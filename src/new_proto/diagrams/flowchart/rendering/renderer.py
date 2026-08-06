from dataclasses import dataclass

from jinja2 import PackageLoader
from wireup import injectable

from ....rendering import JinjaTextRenderer, create_jinja_environment
from ..diagram import Flowchart
from .syntax import mermaid_identifier, mermaid_quote


@dataclass(frozen=True, slots=True)
class FlowchartMmdRenderer:
    template: JinjaTextRenderer[Flowchart]

    def render(self, diagram: Flowchart) -> str:
        return self.template.render(diagram)


@injectable
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
