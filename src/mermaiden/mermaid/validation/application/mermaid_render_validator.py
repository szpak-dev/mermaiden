from collections.abc import Mapping
from dataclasses import dataclass
from xml.etree import ElementTree

from wireup import injectable

from ....core.domain import DiagramView
from ...application import MermaidApplication
from ..domain import (
    MermaidRenderDiagnostic,
    MermaidRenderDiagnosticCode,
    MermaidRenderFailure,
    MermaidRenderReport,
    RendererRuntimeResult,
    RenderValidationRuntime,
)


@injectable
@dataclass(frozen=True, slots=True)
class MermaidRenderValidator:
    renderer: MermaidApplication
    runtime: RenderValidationRuntime

    @property
    def mermaid_version(self) -> str:
        return self.runtime.mermaid_version

    @property
    def mermaid_cli_version(self) -> str:
        return self.runtime.mermaid_cli_version

    def validate(self, diagram: DiagramView) -> MermaidRenderReport:
        validation = diagram.validate()
        if not validation.can_commit:
            return self.failure(
                diagram.kind,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.DIAGRAM_INVALID,
                    "Diagram violates blocking constraints.",
                    "\n".join(
                        f"{violation.code} [{violation.path}]: {violation.message}" for violation in validation.blocking
                    ),
                ),
            )
        try:
            source = self.renderer.render(diagram)
        except Exception as error:
            return self.failure(
                diagram.kind,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.SOURCE_GENERATION_FAILED,
                    "Mermaid source generation failed.",
                    str(error),
                ),
            )
        return self.validate_sources({diagram.kind: source})[0]

    def validate_sources(self, sources: Mapping[str, str]) -> tuple[MermaidRenderReport, ...]:
        try:
            result = self.runtime.render(sources)
        except MermaidRenderFailure as failure:
            return tuple(self.failure(diagram_id, failure) for diagram_id in sources)
        return tuple(self.report(diagram_id, result) for diagram_id in sources)

    def report(self, diagram_id: str, result: RendererRuntimeResult) -> MermaidRenderReport:
        if result.return_code:
            return self.failure(
                diagram_id,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.RENDER_FAILED,
                    self._message(result.output),
                    result.output,
                ),
            )
        if diagram_id not in result.svgs:
            return self.failure(
                diagram_id,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.SVG_MISSING,
                    "Mermaid completed without producing an SVG.",
                ),
            )
        svg = result.svgs[diagram_id]
        if not svg.strip():
            return self.failure(
                diagram_id,
                MermaidRenderFailure(MermaidRenderDiagnosticCode.SVG_EMPTY, "Mermaid produced an empty SVG."),
            )
        try:
            document = ElementTree.fromstring(svg)
        except ElementTree.ParseError as error:
            return self.failure(
                diagram_id,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.SVG_ERROR,
                    "Mermaid produced invalid SVG.",
                    str(error),
                ),
            )
        error_elements = tuple(
            element
            for element in document.iter()
            if {"error-icon", "error-text"}.intersection(element.attrib.get("class", "").split())
        )
        oversized = "Maximum text size in diagram exceeded" in svg
        syntax_error = "Syntax error in text" in svg
        if error_elements or oversized or syntax_error:
            details = " ".join(
                text.strip() for element in error_elements for text in element.itertext() if text.strip()
            )
            return self.failure(
                diagram_id,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.SVG_ERROR,
                    "Mermaid produced an error SVG.",
                    details or ("Maximum text size in diagram exceeded" if oversized else "Syntax error in text"),
                ),
            )
        return MermaidRenderReport(
            diagram_id,
            self.mermaid_version,
            self.mermaid_cli_version,
            svg=svg,
        )

    def failure(self, diagram_id: str, failure: MermaidRenderFailure) -> MermaidRenderReport:
        return MermaidRenderReport(
            diagram_id,
            self.mermaid_version,
            self.mermaid_cli_version,
            diagnostics=(MermaidRenderDiagnostic(failure.code, failure.message, failure.details),),
        )

    def _message(self, output: str) -> str:
        lines = tuple(line.strip() for line in output.splitlines() if line.strip())
        parse_error = next((line for line in lines if line.startswith("Error: Parse error on line ")), "")
        if parse_error:
            line = parse_error.removeprefix("Error: Parse error on line ").rstrip(":")
            expected = next((item for item in lines if " got " in item), "")
            token = expected.rsplit(" got ", 1)[-1].strip("'.") if expected else "unknown token"
            return f"syntax error on line {line} (got {token})"
        return lines[0].removeprefix("Error: ") if lines else "Mermaid rendering failed without diagnostic output."
