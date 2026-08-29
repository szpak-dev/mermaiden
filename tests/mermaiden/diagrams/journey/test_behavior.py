import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestJourney:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("journey")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("set_title", {"title": 'Working "day"'}),
            DiagramCommand("add_section", {"id": "work", "label": "Go to work"}),
            DiagramCommand(
                "add_task",
                {"id": "tea", "label": "Make tea", "score": 5, "actors": ["Me", "Cat"], "section_id": "work"},
            ),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("journey").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
        }
        assert 'title Working "day"' in source
        assert "section Go to work" in source
        assert "Make tea: 5: Me, Cat" in source
        assert application.render(restored) == source

    def test_rejects_invalid_scores_duplicate_sections_and_unknown_sections(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("journey")
        application.apply(diagram, DiagramCommand("add_section", {"id": "work", "label": "Work"}))

        with pytest.raises(UnknownCommand):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_task", {"id": "bad", "label": "Bad", "score": "high", "actors": ["Me"], "section_id": "work"}
                ),
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_section", {"id": "work", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_task",
                    {"id": "orphan", "label": "Orphan", "score": 1, "actors": ["Me"], "section_id": "missing"},
                ),
            )
