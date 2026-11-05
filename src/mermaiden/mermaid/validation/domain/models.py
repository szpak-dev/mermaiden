from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MermaidRenderDiagnosticCode(StrEnum):
    DIAGRAM_INVALID = "diagram_invalid"
    SOURCE_GENERATION_FAILED = "source_generation_failed"
    RENDERER_UNAVAILABLE = "renderer_unavailable"
    VERSION_MISMATCH = "version_mismatch"
    RENDER_TIMEOUT = "render_timeout"
    RENDER_FAILED = "render_failed"
    RENDERER_SETUP_FAILED = "renderer_setup_failed"
    SVG_MISSING = "svg_missing"
    SVG_EMPTY = "svg_empty"
    SVG_ERROR = "svg_error"
    PNG_MISSING = "png_missing"
    PNG_INVALID = "png_invalid"


class PngRenderOptions(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    scale: float = Field(gt=0, allow_inf_nan=False)
    background: Literal["white", "transparent"]


class PngExportOptionsError(ValueError):
    pass


class MermaidPreviewFailure(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class RendererProcessDiagnostic:
    output: str

    @property
    def message(self) -> str:
        lines = tuple(line.strip() for line in self.output.splitlines() if line.strip())
        parse_error = next((line for line in lines if line.startswith("Error: Parse error on line ")), "")
        if parse_error:
            line = parse_error.removeprefix("Error: Parse error on line ").rstrip(":")
            expected = next((item for item in lines if " got " in item), "")
            token = expected.rsplit(" got ", 1)[-1].strip("'.") if expected else "unknown token"
            return f"syntax error on line {line} (got {token})"
        errors = tuple(line for line in lines if "Error:" in line or "error:" in line)
        if errors:
            return errors[0].removeprefix("Error: ")
        return lines[0] if lines else "Mermaid process exited unsuccessfully without diagnostic output."


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


@dataclass(slots=True)
class MermaidRenderFailure(RuntimeError):
    code: MermaidRenderDiagnosticCode
    message: str
    details: str = ""

    def __str__(self) -> str:
        summary = f"{self.code}: {self.message}"
        return f"{summary}\n{self.details}" if self.details else summary
