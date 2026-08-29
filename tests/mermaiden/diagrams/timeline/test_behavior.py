import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestTimeline:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("timeline")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("set_title", {"title": 'Project "history"'}),
            DiagramCommand("add_section", {"id": "foundation", "label": "Foundation"}),
            DiagramCommand("add_period", {"id": "year", "label": "2026", "section_id": "foundation"}),
            DiagramCommand("add_event", {"id": "release", "label": "First release", "period_id": "year"}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("timeline").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'title Project "history"' in source
        assert "section Foundation" in source
        assert "2026 : First release" in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_periods(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("timeline")
        application.apply(diagram, DiagramCommand("add_section", {"id": "section", "label": "Section"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"missing": True}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_section", {"id": "section", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_event", {"id": "event", "label": "Event", "period_id": "missing"})
            )
