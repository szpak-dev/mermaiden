from collections.abc import Mapping
from dataclasses import dataclass
from xml.etree import ElementTree

from jinja2 import TemplateError
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
from ..domain.models import RendererProcessDiagnostic


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
        except TemplateError as error:
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
        if not sources:
            return ()
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
                    RendererProcessDiagnostic(result.output).message,
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
            ElementTree.fromstring(svg)
        except ElementTree.ParseError as error:
            return self.failure(
                diagram_id,
                MermaidRenderFailure(
                    MermaidRenderDiagnosticCode.SVG_ERROR,
                    "Mermaid produced invalid SVG.",
                    str(error),
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
