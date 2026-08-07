from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ....core.diagram import DiagramView
from ...rendering import DiagramMmdRenderer, JinjaDiagramMmdRenderer
from ..diagram import SequenceDiagram


@injectable(as_type=DiagramMmdRenderer, qualifier="sequence")
@dataclass(frozen=True, slots=True)
class SequenceMmdRenderer(JinjaDiagramMmdRenderer):
    diagram_type: ClassVar[type[DiagramView]] = SequenceDiagram
    template_package: ClassVar[str] = "new_proto.diagrams.sequence.rendering"
    template_namespace: ClassVar[str] = "sequence"
