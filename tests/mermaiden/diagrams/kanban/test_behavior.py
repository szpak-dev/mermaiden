import json

import pytest

from mermaiden import Application


class TestKanban:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("kanban")
        commands = (
            ("configure", {"padding": 12, "sectionWidth": 240, "ticketBaseUrl": "https://tracker/"}),
            ("add_column", {"id": "todo_example", "label": 'To "do"'}),
            (
                "add_task",
                {
                    "id": "docs_example",
                    "label": "Write docs_example",
                    "column_id": "todo_example",
                    "assigned": "Ada",
                    "ticket": "DOC-1",
                    "priority": "High",
                },
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("kanban").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'todo_example["To \\"do\\""]' in source
        assert 'docs_example["Write docs_example"]' in source
        assert 'assigned: "Ada"' in source
        assert 'ticket: "DOC-1"' in source
        assert 'priority: "High"' in source
        assert application.render(restored) == source

    def test_rejects_invalid_priorities_duplicates_and_unknown_columns(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("kanban")
        application.execute(diagram, "add_column", {"id": "todo_example", "label": "Todo"})
        with pytest.raises(RuntimeError, match=r"'add_task' has invalid arguments"):
            application.execute(
                diagram,
                "add_task",
                {"id": "bad_example", "label": "Bad", "column_id": "todo_example", "priority": "Urgent"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_column", {"id": "todo_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_task", {"id": "orphan_example", "label": "Orphan", "column_id": "missing"}
            )
