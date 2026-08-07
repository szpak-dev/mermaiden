import base64
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from wireup import injectable

from ..core.diagram import DiagramView


@injectable
@dataclass(frozen=True, slots=True)
class MermaidRenderer:
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
                "mermaid_quote": self._quote,
                "tree_label": self._tree_label,
            }
        )
        object.__setattr__(self, "environment", environment)

    def render(self, diagram: DiagramView) -> str:
        body = self.environment.get_template("templates/document.mmd.j2").render(
            diagram=diagram,
            template_prefix=self._template_prefix(diagram),
        )
        source = self._canonical_text(body)
        return self._wrap(source) if self.wrap else source

    @staticmethod
    def _template_prefix(diagram: DiagramView) -> str:
        return f"templates/syntax/{diagram.kind}"

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
    def _wrap(body: str) -> str:
        return f"---\nconfig:\n  wrap: true\n---\n{body}"
