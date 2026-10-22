import json

import pytest

from mermaiden import Application


class TestTimeline:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("timeline")
        commands = (
            ("configure", {"wrap": False}),
            ("set_title", {"title": 'Project "history"'}),
            ("add_section", {"id": "foundation_example", "label": "Foundation"}),
            ("add_period", {"id": "year_example", "label": "2026", "section_id": "foundation_example"}),
            ("add_event", {"id": "release_example", "label": "First release_example", "period_id": "year_example"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("timeline").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'title Project "history"' in source
        assert "section Foundation" in source
        assert "2026 : First release_example" in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_periods(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("timeline")
        application.execute(diagram, "add_section", {"id": "section_example", "label": "Section"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"missing_example": True})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_section", {"id": "section_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_event", {"id": "event_example", "label": "Event", "period_id": "missing_example"}
            )
