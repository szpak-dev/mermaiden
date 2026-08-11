import base64
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from wireup import injectable

from ..core.diagram import DiagramView
from .domain import MermaidPreview


@injectable
@dataclass(frozen=True, slots=True)
class MermaidApplication:
    wrap: bool = field(default=True, init=False)
    environment: Environment = field(init=False)

    def __post_init__(self) -> None:
        environment = Environment(
            loader=FileSystemLoader(Path(__file__).parent),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            newline_sequence="\n",
        )
        environment.filters.update(
            {
                "mermaid_id": self._identifier,
                "mermaid_number": self._number,
                "mermaid_quote": self._quote,
                "tree_label": self._tree_label,
            }
        )
        object.__setattr__(self, "environment", environment)

    def render(self, diagram: DiagramView) -> str:
        body = self.environment.get_template(self.document_template(diagram)).render(
            diagram=diagram,
            template_prefix=self._template_prefix(diagram),
        )
        source = self._canonical_text(body)
        return self._wrap(source, diagram.mermaid_configuration) if self.wrap else source


    @staticmethod
    def _template_prefix(diagram: DiagramView) -> str:
        return f"templates/syntax/{diagram.kind}"

    def document_template(self, diagram: DiagramView) -> str:
        return f"{self._template_prefix(diagram)}/document.mmd.j2"

    @staticmethod
    def _identifier(value: object, namespace: str) -> str:
        text = str(value)
        identifier = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
        token = (
            f"v_{text}"
            if identifier.fullmatch(text)
            else f"b_{base64.b32encode(text.encode()).decode().rstrip('=').lower()}"
        )
        return f"{namespace}_{token}"

    @staticmethod
    def _quote(value: object) -> str:
        return json.dumps(str(value), ensure_ascii=False)

    @staticmethod
    def _number(value: float | int) -> str:
        return str(int(value)) if isinstance(value, float) and value.is_integer() else str(value)

    @staticmethod
    def _tree_label(value: object) -> str:
        text = str(value)
        if not text or text != text.strip() or "  " in text or any(token in text for token in ('"', ":::", "##")):
            return json.dumps(text, ensure_ascii=False)
        return text

    @staticmethod
    def _canonical_text(value: str) -> str:
        normalized = value.replace("\r\n", "\n").replace("\r", "\n")
        lines = (line.rstrip() for line in normalized.split("\n"))
        return "\n".join(line for line in lines if line).rstrip("\n") + "\n"

    @staticmethod
    def _wrap(body: str, configuration: Mapping[str, object]) -> str:
        entries = "".join(
            f"  {key}: {json.dumps(value, ensure_ascii=False)}\n"
            for key, value in configuration.items()
            if key != "wrap"
        )
        return f"---\nconfig:\n  wrap: true\n{entries}---\n{body}"


@injectable
@dataclass(frozen=True, slots=True)
class MermaidPreviewApplication:
    preview: MermaidPreview
    renderer: MermaidApplication

    def write(self, diagrams: Sequence[DiagramView], output: Path) -> Path:
        return self.preview.write_sources({diagram.kind: self.renderer.render(diagram) for diagram in diagrams}, output)

    def write_sources(self, sources: Mapping[str, str], output: Path) -> Path:
        return self.preview.write_sources(sources, output)
