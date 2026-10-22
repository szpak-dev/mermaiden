import json

import pytest

from mermaiden import Application


class TestGantt:
    def test_exercises_milestones_markers_date_format_and_every_public_command(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gantt")
        commands = (
            ("configure", {"barHeight": 24, "topAxis": True}),
            ("set_title", {"title": 'Release "plan"'}),
            ("set_date_format", {"date_format": "YYYY-MM-DD"}),
            ("add_section", {"id": "delivery_example", "label": "Delivery"}),
            (
                "add_task",
                {
                    "id": "design_example",
                    "label": "Design",
                    "section_id": "delivery_example",
                    "status": "done",
                    "start": {"kind": "date", "date": "2026-08-01"},
                    "finish": {"kind": "duration", "amount": 2, "unit": "days"},
                },
            ),
            (
                "add_milestone",
                {
                    "id": "release_example",
                    "label": "Release",
                    "section_id": "delivery_example",
                    "start": {"kind": "date", "date": "2026-08-03"},
                    "finish": {"kind": "duration", "amount": 0},
                },
            ),
            ("add_marker", {"id": "today_example", "label": "Today", "date": "2026-08-02"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("gantt").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        for fragment in (
            'title Release "plan"',
            "dateFormat YYYY-MM-DD",
            "section Delivery",
            "Design : done, design_example, 2026-08-01, 2d",
            "Release : milestone, release_example, 2026-08-03, 0d",
            "vert 2026-08-02 : Today",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicate_ids_and_unknown_sections(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("gantt")
        application.execute(diagram, "add_section", {"id": "delivery_example", "label": "Delivery"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"barHeight": "large"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_section", {"id": "delivery_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_task",
                {
                    "id": "task_example",
                    "label": "Task",
                    "section_id": "missing_example",
                    "start": {"kind": "date", "date": "2026-08-01"},
                    "finish": {"kind": "duration", "amount": 1},
                },
            )
        for arguments in (
            {"id": "old_example", "label": "Old", "section_id": "delivery_example", "metadata": ["2026-08-01", "1d"]},
            {
                "id": "bad_example",
                "label": "Bad",
                "section_id": "delivery_example",
                "start": {"kind": "date", "date": ""},
                "finish": {"kind": "duration", "amount": 1},
            },
        ):
            with pytest.raises(RuntimeError, match=r"invalid arguments"):
                application.execute(diagram, "add_task", arguments)
