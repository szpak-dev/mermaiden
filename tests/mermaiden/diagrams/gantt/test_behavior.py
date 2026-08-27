import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestGantt:
    def test_exercises_milestones_markers_date_format_and_every_public_command(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gantt")

        commands = (
            DiagramCommand("configure", {"barHeight": 24, "topAxis": True}),
            DiagramCommand("set_title", {"title": 'Release "plan"'}),
            DiagramCommand("set_date_format", {"date_format": "YYYY-MM-DD"}),
            DiagramCommand("add_section", {"id": "delivery", "label": "Delivery"}),
            DiagramCommand(
                "add_task",
                {
                    "id": "design",
                    "label": "Design",
                    "metadata": ["done", "design", "2026-08-01", "2d"],
                    "section_id": "delivery",
                },
            ),
            DiagramCommand(
                "add_milestone",
                {
                    "id": "release",
                    "label": "Release",
                    "metadata": ["2026-08-03", "0d"],
                    "section_id": "delivery",
                },
            ),
            DiagramCommand("add_marker", {"id": "today", "label": "Today", "date": "2026-08-02"}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("gantt").commands) == {item.operation for item in commands} | {
            "remove_element"
        }
        for fragment in (
            'title Release "plan"',
            "dateFormat YYYY-MM-DD",
            "section Delivery",
            "Design : done, design, 2026-08-01, 2d",
            "Release : milestone, 2026-08-03, 0d",
            "vert 2026-08-02 : Today",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicate_ids_and_unknown_sections(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gantt")
        application.apply(diagram, DiagramCommand("add_section", {"id": "delivery", "label": "Delivery"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"barHeight": "large"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_section", {"id": "delivery", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_task",
                    {"id": "task", "label": "Task", "metadata": ["2026-08-01", "1d"], "section_id": "missing"},
                ),
            )
