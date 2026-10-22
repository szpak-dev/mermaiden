import json

import pytest

from mermaiden import Application


class TestJourney:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("journey")
        commands = (
            ("configure", {"wrap": False}),
            ("set_title", {"title": 'Working "day"'}),
            ("add_section", {"id": "work_example", "label": "Go to work_example"}),
            (
                "add_task",
                {
                    "id": "tea_example",
                    "label": "Make tea_example",
                    "score": 5,
                    "actors": ["Me", "Cat"],
                    "section_id": "work_example",
                },
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("journey").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'title Working "day"' in source
        assert "section Go to work_example" in source
        assert "Make tea_example: 5: Me, Cat" in source
        assert application.render(restored) == source

    def test_rejects_invalid_scores_duplicate_sections_and_unknown_sections(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("journey")
        application.execute(diagram, "add_section", {"id": "work_example", "label": "Work"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_task",
                {"id": "bad_example", "label": "Bad", "score": "high", "actors": ["Me"], "section_id": "work_example"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_section", {"id": "work_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_task",
                {
                    "id": "orphan_example",
                    "label": "Orphan",
                    "score": 1,
                    "actors": ["Me"],
                    "section_id": "missing_example",
                },
            )
