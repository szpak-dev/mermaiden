from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class MermaidRenderDiagnosticCode(StrEnum):
    DIAGRAM_INVALID = "diagram_invalid"
    SOURCE_GENERATION_FAILED = "source_generation_failed"
    RENDERER_UNAVAILABLE = "renderer_unavailable"
    VERSION_MISMATCH = "version_mismatch"
    RENDER_TIMEOUT = "render_timeout"
    RENDER_FAILED = "render_failed"
    SVG_MISSING = "svg_missing"
    SVG_EMPTY = "svg_empty"
    SVG_ERROR = "svg_error"


@dataclass(frozen=True, slots=True)
class MermaidRenderDiagnostic:
    code: MermaidRenderDiagnosticCode
    message: str
    details: str = ""


@dataclass(frozen=True, slots=True)
class MermaidRenderReport:
    diagram_id: str
    mermaid_version: str
    mermaid_cli_version: str
    svg: str = ""
    diagnostics: tuple[MermaidRenderDiagnostic, ...] = ()

    @property
    def success(self) -> bool:
        return bool(self.svg.strip()) and not self.diagnostics


@dataclass(frozen=True, slots=True)
class RendererRuntimeResult:
    return_code: int
    svgs: Mapping[str, str]
    output: str = ""


@dataclass(frozen=True, slots=True)
class MermaidRenderFailure(RuntimeError):
    code: MermaidRenderDiagnosticCode
    message: str
    details: str = ""

    def __str__(self) -> str:
        return self.message
