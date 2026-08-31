from dataclasses import dataclass, field

from wireup import injectable

from ..core.domain import DiagramView
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
