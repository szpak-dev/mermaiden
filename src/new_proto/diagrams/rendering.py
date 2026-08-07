from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar

from wireup import injectable

from ..core.diagram import DiagramView
from ..core.error import OperationError


class DiagramMmdRenderer(ABC):
    diagram_type: ClassVar[type[DiagramView]]

    def can_render(self, diagram: DiagramView) -> bool:
        return isinstance(diagram, self.diagram_type)

    def render_body(self, diagram: DiagramView) -> str:
        if not self.can_render(diagram):
            raise OperationError(f"Mermaid renderer cannot render diagram kind '{diagram.kind}'.")
        return self._render(diagram)

    @abstractmethod
    def _render(self, diagram: DiagramView) -> str: ...


@injectable
@dataclass(frozen=True, slots=True)
class MermaidRenderer:
    renderers: Sequence[DiagramMmdRenderer]
    wrap: bool = True

    def render(self, diagram: DiagramView) -> str:
        renderer = next((item for item in self.renderers if item.can_render(diagram)), None)
        if renderer is None:
            raise OperationError(f"No Mermaid renderer is registered for diagram kind '{diagram.kind}'.")
        return self._wrap(renderer.render_body(diagram))

    def _wrap(self, body: str) -> str:
        if not self.wrap:
            return body
        return f"---\nconfig:\n  wrap: true\n---\n{body}"


__all__ = ["DiagramMmdRenderer", "MermaidRenderer"]
