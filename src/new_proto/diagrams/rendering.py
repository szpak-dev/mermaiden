from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from wireup import injectable

from ..core.diagram import DiagramView
from ..core.error import OperationError


class DiagramMmdRenderer(ABC):
    @abstractmethod
    def can_render(self, diagram: DiagramView) -> bool: ...

    @abstractmethod
    def render_body(self, diagram: DiagramView) -> str: ...


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
