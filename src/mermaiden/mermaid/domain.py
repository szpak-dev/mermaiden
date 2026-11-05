from base64 import b64encode
from collections.abc import Mapping
from dataclasses import dataclass
from html import escape
from pathlib import Path

from wireup import injectable

from .validation.application.mermaid_render_validator import MermaidRenderValidator
from .validation.domain.models import MermaidPreviewFailure


@injectable
@dataclass(frozen=True, slots=True)
class MermaidPreview:
    validator: MermaidRenderValidator

    def write_sources(self, sources: Mapping[str, str], output: Path) -> Path:
        reports = self.validator.validate_sources(sources)
        failures = tuple(diagnostic for report in reports for diagnostic in report.diagnostics)
        if failures:
            raise MermaidPreviewFailure(
                "\n".join(
                    f"{report.diagram_id}: {failure.code}: {failure.message} {failure.details}".rstrip()
                    for report in reports
                    for failure in report.diagnostics
                )
            )
        sections = "\n".join(
            self._source_section(report.diagram_id, sources[report.diagram_id], report.svg) for report in reports
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self._document(sections), encoding="utf-8")
        return output

    def _source_section(self, name: str, source: str, svg: str) -> str:
        encoded = b64encode(svg.encode("utf-8")).decode("ascii")
        return (
            f"<section><h2>{escape(name)}</h2>"
            f'<img alt="{escape(name, quote=True)}" src="data:image/svg+xml;base64,{encoded}">'
            f"<details><summary>Mermaid source</summary><pre>{escape(source)}</pre></details></section>"
        )

    def _document(self, sections: str) -> str:
        return f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<title>Mermaid previews</title>
<style>
body {{ font-family: sans-serif; margin: 2rem; }} section {{ margin-block: 3rem; }} img {{ max-width: 100%; }}
</style>
<body>
{sections}
</body>
</html>
"""
