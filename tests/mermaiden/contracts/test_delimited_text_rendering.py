from xml.etree import ElementTree

import pytest

from mermaiden import Application


class TestDelimitedTextRendering:
    @pytest.mark.integration
    @pytest.mark.parametrize("kind", ("journey", "timeline"))
    @pytest.mark.parametrize(
        "label",
        (
            "Example: detail; A, B",
            "literal &amp; &#34; #59;",
            "<br> <b>example</b>",
            'Example "quotes" %22 %u0041',
            "title example",
            "section example",
            "Example — Łódź 🙂",
            "#" * 70,
            "🙂" * 80,
        ),
    )
    def test_literal_text_survives_grammar_layout_and_restore(self, kind: str, label: str) -> None:
        with Application.create() as application:
            diagram = application.create_diagram(kind)
            application.execute(diagram, "set_title", {"title": label})
            application.execute(diagram, "add_section", {"id": "section_example", "label": label})
            if kind == "journey":
                application.execute(
                    diagram,
                    "add_task",
                    {
                        "id": "task_example",
                        "label": label,
                        "score": 3,
                        "actors": [label],
                        "section_id": "section_example",
                    },
                )
            else:
                application.execute(
                    diagram,
                    "add_period",
                    {"id": "period_example", "label": label, "section_id": "section_example"},
                )
                application.execute(
                    diagram, "add_event", {"id": "event_example", "label": label, "period_id": "period_example"}
                )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            restored = application.restore(before)
            report = application.validate_render(restored)
            assert report.success, report.diagnostics
            svg = ElementTree.fromstring(report.svg)
            texts = tuple(
                " ".join(" ".join(element.itertext()).split())
                for element in svg.iter("{http://www.w3.org/2000/svg}text")
            )
            assert texts.count(label) >= (3 if kind == "journey" else 4)
            if kind == "journey":
                actors = "".join(
                    "".join(element.itertext())
                    for element in svg.iter("{http://www.w3.org/2000/svg}text")
                    if element.attrib.get("class") == "legend"
                )
                assert actors == label
            assert application.snapshot(restored).to_dict() == before
            assert application.render(restored) == source


class TestNamedSourceValidation:
    @pytest.mark.integration
    def test_error_svg_is_rejected_then_valid_sources_recover_in_order(self) -> None:
        with Application.create() as application:
            oversized = '---\nconfig:\n  htmlLabels: false\n---\nclassDiagram\nclass Example["' + "x" * 60000 + '"]\n'
            failed = application.validate_sources({"oversized_example": oversized})
            assert len(failed) == 1
            assert failed[0].diagram_id == "oversized_example"
            assert not failed[0].success
            assert failed[0].diagnostics[0].code == "svg_error"
            assert "Maximum text size" in failed[0].diagnostics[0].details
            sources = {"second_example": "flowchart LR\nA[Example]\n", "first_example": "classDiagram\nclass Example\n"}
            reports = application.validate_sources(sources)
            assert tuple(report.diagram_id for report in reports) == tuple(sources)
            for report in reports:
                assert report.success, report.diagnostics
                assert report.mermaid_version == application.mermaid_version
                assert report.mermaid_cli_version == application.mermaid_cli_version
                assert ElementTree.fromstring(report.svg).tag == "{http://www.w3.org/2000/svg}svg"

    def test_empty_sources_are_a_noop_and_closed_handle_is_rejected(self) -> None:
        application = Application.create()
        assert application.validate_sources({}) == ()
        application.close()
        with pytest.raises(RuntimeError, match="closed"):
            application.validate_sources({})
