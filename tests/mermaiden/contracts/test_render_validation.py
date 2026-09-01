import pytest

from mermaiden import Application


class TestRenderValidation:
    def test_draft_diagram_can_be_persisted_but_not_rendered(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")

        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(payload)
        report = application.validate_render(diagram)

        assert application.snapshot(restored).to_dict() == payload
        assert not report.success
        assert report.diagram_id == "sequenceDiagram"
        assert report.mermaid_version == "11.16.0"
        assert report.diagnostics[0].code == "diagram_invalid"
        assert "Diagram requires at least one element" in report.diagnostics[0].details
        with pytest.raises(RuntimeError, match="Cannot render invalid diagram 'sequenceDiagram'"):
            application.render(restored)

    def test_a_valid_snapshot_tampered_into_an_invalid_state_cannot_be_restored(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(
            diagram,
            "add_participant",
            {"id": "participant_example", "label": "Participant Example"},
        )
        payload = application.snapshot(diagram).to_dict()
        payload["elements"] = []

        with pytest.raises(RuntimeError, match="Cannot restore invalid diagram 'sequenceDiagram'"):
            application.restore(payload)

    def test_full_render_validation_is_a_non_mutating_application_operation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(
            diagram,
            "add_participant",
            {"id": "participant_example", "label": "Participant Example"},
        )
        before = application.snapshot(diagram).to_dict()

        report = application.validate_render(diagram)

        assert report.success
        assert report.diagram_id == "sequenceDiagram"
        assert report.mermaid_version == "11.16.0"
        assert report.svg.startswith("<svg")
        assert not report.diagnostics
        assert application.snapshot(diagram).to_dict() == before
