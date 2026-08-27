from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from wireup import injectable

from ..core.diagram import DiagramView
from .domain import MermaidPreview
from .templates import MermaidSourceFormatter, MermaidTemplateRenderer


@injectable
@dataclass(frozen=True, slots=True)
class MermaidApplication:
    templates: MermaidTemplateRenderer
    source: MermaidSourceFormatter
    wrap: bool = field(default=True, init=False)

    def render(self, diagram: DiagramView) -> str:
        body = self.source.canonicalize(self.templates.render(diagram))
        return self.source.wrap(body, diagram.mermaid_configuration) if self.wrap else body


@injectable
@dataclass(frozen=True, slots=True)
class MermaidPreviewApplication:
    preview: MermaidPreview
    renderer: MermaidApplication

    def write(self, diagrams: Sequence[DiagramView], output: Path) -> Path:
        return self.preview.write_sources({diagram.kind: self.renderer.render(diagram) for diagram in diagrams}, output)

    def write_sources(self, sources: Mapping[str, str], output: Path) -> Path:
        return self.preview.write_sources(sources, output)
