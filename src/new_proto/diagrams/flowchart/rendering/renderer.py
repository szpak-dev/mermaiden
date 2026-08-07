from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..diagram import Flowchart
from .syntax import mermaid_identifier, mermaid_quote


@injectable(as_type=DiagramMmdRenderer, qualifier="flowchart")
@dataclass(frozen=True, slots=True)
class FlowchartMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = Flowchart

    template_package: ClassVar[str] = "new_proto.diagrams.flowchart.rendering"
    template_namespace: ClassVar[str] = "flowchart"
    template_filters: ClassVar = {"mmd_id": mermaid_identifier, "mmd_quote": mermaid_quote}
