from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import ClassVar, cast

from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from wireup import injectable

from ..core.diagram import DiagramView
from ..core.error import OperationError
from ..rendering.jinja import JinjaTextRenderer, create_jinja_environment


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


@dataclass(frozen=True, slots=True)
class JinjaDiagramMmdRenderer(DiagramMmdRenderer):
    template: JinjaTextRenderer[object] = field(init=False)
    template_package: ClassVar[str]
    template_namespace: ClassVar[str]
    template_filters: ClassVar[Mapping[str, Callable[..., object]]] = {}

    def __post_init__(self) -> None:
        environment = create_jinja_environment(
            ChoiceLoader(
                [
                    PackageLoader("new_proto.rendering", "templates"),
                    PrefixLoader({self.template_namespace: PackageLoader(self.template_package, "templates")}),
                ]
            ),
            filters=self.template_filters,
        )
        cast(dict[str, object], environment.globals)["template_prefix"] = self.template_namespace
        object.__setattr__(self, "template", JinjaTextRenderer[object](environment, "diagram.mmd.j2"))

    def _render(self, diagram: DiagramView) -> str:
        return self.template.render(self.model(diagram))

    def model(self, diagram: DiagramView) -> object:
        return diagram


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
