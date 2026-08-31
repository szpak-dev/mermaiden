from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from wireup import injectable

from ...core.domain import DiagramView
from ..application import MermaidApplication
from ..domain import MermaidPreview


@injectable
@dataclass(frozen=True, slots=True)
class MermaidPreviewApplication:
    preview: MermaidPreview
    renderer: MermaidApplication

    def write(self, diagrams: Sequence[DiagramView], output: Path) -> Path:
        return self.preview.write_sources({diagram.kind: self.renderer.render(diagram) for diagram in diagrams}, output)

    def write_sources(self, sources: Mapping[str, str], output: Path) -> Path:
        return self.preview.write_sources(sources, output)
