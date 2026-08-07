from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..diagram import Architecture


@injectable(as_type=DiagramMmdRenderer, qualifier="architecture")
@dataclass(frozen=True, slots=True)
class ArchitectureMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = Architecture
    template_package: ClassVar[str] = "new_proto.diagrams.architecture.rendering"
