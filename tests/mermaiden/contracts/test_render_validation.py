from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import pytest

from mermaiden.application import Application, DiagramCommand
from mermaiden.core import Annotation, ChangeReport, Diagram, Element, Relation, ValidationReport
from mermaiden.mermaid.application import MermaidApplication
from mermaiden.mermaid.templates import MermaidSourceFormatter, MermaidTemplateRenderer, MermaidValueFormatter
from mermaiden.mermaid.validation import (
    MermaidCliResult,
    MermaidRenderDiagnosticCode,
    MermaidRenderValidator,
)


@dataclass(frozen=True, slots=True)
class ExampleMermaidCli:
    result: MermaidCliResult
    version: str = "11.16.0"

    def render(self, sources: Mapping[str, str]) -> MermaidCliResult:
        if self.result.return_code == 0 and self.result.svgs == {"example": "dynamic"}:
            return MermaidCliResult(0, {diagram_id: "<svg></svg>" for diagram_id in sources})
        return self.result


@dataclass(frozen=True, slots=True)
class ExampleDiagram(Diagram):
    @property
    def kind(self) -> str:
        return "example-diagram"

    @property
    def mermaid_configuration(self) -> Mapping[str, object]:
        return {}

    @property
    def root_elements(self) -> Sequence[Element]:
        return ()

    def find_element(self, id: str) -> Element | None:
        return None

    def walk_elements(self, parent_id: str = "") -> Sequence[Element]:
        return ()

    def find_relations(self, element_id: str = "") -> Sequence[Relation]:
        return ()

    def find_annotations(self, target_id: str = "") -> Sequence[Annotation]:
        return ()

    def validate(self) -> ValidationReport:
        return ValidationReport()

    def remove_element(self, id: str, *, cascade: bool = False) -> ChangeReport:
        raise NotImplementedError

    def remove_relation(self, id: str) -> ChangeReport:
        raise NotImplementedError

    def remove_annotation(self, id: str) -> ChangeReport:
        raise NotImplementedError


def _validator(result: MermaidCliResult) -> MermaidRenderValidator:
    renderer = MermaidApplication(
        MermaidTemplateRenderer(MermaidValueFormatter()),
        MermaidSourceFormatter(),
    )
    return MermaidRenderValidator(renderer, ExampleMermaidCli(result))


def test_application_reports_source_generation_failure_through_its_public_contract() -> None:
    report = Application.create().validate_render(ExampleDiagram())

    assert not report.success
    assert report.diagram_id == "example-diagram"
    assert report.mermaid_version == "11.16.0"
    assert report.diagnostics[0].code is MermaidRenderDiagnosticCode.SOURCE_GENERATION_FAILED
    assert report.diagnostics[0].message == "Mermaid source generation failed."


def test_full_render_validation_reports_an_unavailable_renderer() -> None:
    report = _validator(MermaidCliResult(None, {}, "example executable is unavailable")).validate_sources(
        {"example-diagram": "example source"}
    )[0]

    assert not report.success
    assert report.diagnostics[0].code is MermaidRenderDiagnosticCode.RENDERER_UNAVAILABLE
    assert report.diagnostics[0].message == "Mermaid CLI could not be started."
    assert report.diagnostics[0].details == "example executable is unavailable"


def test_full_render_validation_returns_structured_rendering_diagnostics() -> None:
    report = _validator(MermaidCliResult(1, {}, "Error: example layout conflict")).validate_sources(
        {"example-diagram": "example source"}
    )[0]

    assert not report.success
    assert report.svg == ""
    assert report.diagnostics[0].code is MermaidRenderDiagnosticCode.RENDER_FAILED
    assert report.diagnostics[0].message == "example layout conflict"
    assert report.diagnostics[0].details == "Error: example layout conflict"


@pytest.mark.parametrize(
    ("svgs", "code", "message"),
    (
        ({}, MermaidRenderDiagnosticCode.SVG_MISSING, "without producing an SVG"),
        ({"example-diagram": ""}, MermaidRenderDiagnosticCode.SVG_EMPTY, "empty SVG"),
        (
            {"example-diagram": "<svg>Syntax error in text</svg>"},
            MermaidRenderDiagnosticCode.SVG_ERROR,
            "syntax-error SVG",
        ),
    ),
)
def test_full_render_validation_requires_a_non_error_svg(
    svgs: Mapping[str, str],
    code: MermaidRenderDiagnosticCode,
    message: str,
) -> None:
    report = _validator(MermaidCliResult(0, svgs)).validate_sources(
        {"example-diagram": "example source"}
    )[0]

    assert not report.success
    assert report.diagnostics[0].code is code
    assert message in report.diagnostics[0].message


def test_full_render_validation_does_not_mutate_the_diagram() -> None:
    application = Application.create()
    diagram = application.create_diagram("sequenceDiagram")
    application.apply(
        diagram,
        DiagramCommand("add_participant", {"id": "participant_example", "label": "Participant Example"}),
    )
    before = application.snapshot(diagram).to_dict()

    report = _validator(MermaidCliResult(0, {"example": "dynamic"})).validate(diagram)

    assert report.success
    assert application.snapshot(diagram).to_dict() == before


def test_full_render_validation_is_available_for_every_advertised_diagram_kind() -> None:
    application = Application.create()
    validator = _validator(MermaidCliResult(0, {"example": "dynamic"}))

    reports = tuple(
        validator.validate(application.create_diagram(info.id))
        for info in application.available_diagrams()
    )

    assert {report.diagram_id for report in reports} == {
        info.id for info in application.available_diagrams()
    }
    assert all(report.success for report in reports)


def test_full_render_validation_returns_the_svg_and_compatible_mermaid_version() -> None:
    report = _validator(
        MermaidCliResult(0, {"example-diagram": '<svg xmlns="http://www.w3.org/2000/svg"></svg>'})
    ).validate_sources({"example-diagram": "example source"})[0]

    assert report.success
    assert report.diagram_id == "example-diagram"
    assert report.mermaid_version == "11.16.0"
    assert report.svg.startswith("<svg")
    assert not report.diagnostics
