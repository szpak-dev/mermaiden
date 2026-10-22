import json
from typing import Any

import pytest

from mermaiden import Application


class TestC4:
    def test_exercises_every_element_and_configuration_command(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.execute(diagram, "configure", {"c4ShapeInRow": 3})
        application.execute(diagram, "add_person", {"id": "user_example", "label": "User"})
        application.execute(diagram, "add_system", {"id": "app_example", "label": "Application"})
        application.execute(
            diagram,
            "add_database",
            {"id": "database_example", "label": "Database", "description": "Stores data", "technology": "SQL"},
        )
        application.execute(
            diagram,
            "add_queue",
            {
                "id": "events_example",
                "label": "Events",
                "description": "Publishes events_example",
                "technology": "Kafka",
            },
        )
        application.execute(
            diagram,
            "add_relationship",
            {
                "id": "relationship_example",
                "source_id": "user_example",
                "target_id": "app_example",
                "label": "Uses Example",
            },
        )
        application.execute(
            diagram, "set_relationship_label_offset", {"id": "relationship_example", "offset_x": 12, "offset_y": -6}
        )
        source = application.render(diagram)
        assert '"c4ShapeInRow": 3' in source
        assert 'SystemDb(database_example, "Database", "Stores data", "SQL")' in source
        assert 'SystemQueue(events_example, "Events", "Publishes events_example", "Kafka")' in source
        assert set(application.diagram_description("C4Context").commands) == {
            "configure",
            "add_database",
            "add_person",
            "add_queue",
            "add_relationship",
            "add_system",
            "set_relationship_label_offset",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }

    def _diagram_with_relationship(self) -> tuple[Application, Any]:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.execute(diagram, "add_person", {"id": "user_example", "label": "User"})
        application.execute(diagram, "add_system", {"id": "app_example", "label": "Application"})
        application.execute(
            diagram,
            "add_relationship",
            {"id": "uses_example", "source_id": "user_example", "target_id": "app_example", "label": "Uses"},
        )
        return (application, diagram)

    def test_rejects_duplicate_elements_and_unknown_relationship_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.execute(diagram, "add_person", {"id": "user_example", "label": "User"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_person", {"id": "user_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_relationship",
                {"id": "uses_example", "source_id": "user_example", "target_id": "missing_example", "label": "Uses"},
            )

    @pytest.mark.parametrize(
        ("direction", "mermaid_function"),
        (("Rel", "Rel"), ("Rel_R", "Rel_R"), ("Rel_L", "Rel_L"), ("Rel_Up", "Rel_Up"), ("Rel_Down", "Rel_Down")),
    )
    def test_renders_and_restores_every_relationship_direction(self, direction: str, mermaid_function: str) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.execute(diagram, "add_person", {"id": "user_example", "label": "User"})
        application.execute(diagram, "add_system", {"id": "app_example", "label": "Application"})
        application.execute(
            diagram,
            "add_relationship",
            {
                "id": "uses_example",
                "source_id": "user_example",
                "target_id": "app_example",
                "label": "Uses",
                "direction": direction,
            },
        )
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert f'{mermaid_function}(user_example, app_example, "Uses")' in source
        assert application.render(restored) == source

    def test_rejects_an_unknown_relationship_direction(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        with pytest.raises(RuntimeError, match=r"'add_relationship' has invalid arguments"):
            application.execute(
                diagram,
                "add_relationship",
                {
                    "id": "uses_example",
                    "source_id": "user_example",
                    "target_id": "app_example",
                    "label": "Uses",
                    "direction": "Rel_Sideways",
                },
            )

    @pytest.mark.parametrize(("offset_x", "offset_y"), ((16, 8), (-16, -8), (-16, 8)))
    def test_renders_and_restores_relationship_label_offsets(self, offset_x: int, offset_y: int) -> None:
        application, diagram = self._diagram_with_relationship()
        application.execute(
            diagram, "set_relationship_label_offset", {"id": "uses_example", "offset_x": offset_x, "offset_y": offset_y}
        )
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert f'UpdateRelStyle(user_example, app_example, $offsetX="{offset_x}", $offsetY="{offset_y}")' in source
        assert application.render(restored) == source

    def test_renders_offsets_after_every_relationship_declaration(self) -> None:
        application, diagram = self._diagram_with_relationship()
        application.execute(diagram, "add_system", {"id": "database_example", "label": "Database"})
        application.execute(
            diagram,
            "add_relationship",
            {"id": "reads_example", "source_id": "app_example", "target_id": "database_example", "label": "Reads"},
        )
        application.execute(
            diagram, "set_relationship_label_offset", {"id": "uses_example", "offset_x": 12, "offset_y": -6}
        )
        source = application.render(diagram)
        assert source.index('Rel(app_example, database_example, "Reads")') < source.index(
            "UpdateRelStyle(user_example, app_example"
        )

    def test_resetting_both_offsets_removes_the_style_statement(self) -> None:
        application, diagram = self._diagram_with_relationship()
        application.execute(
            diagram, "set_relationship_label_offset", {"id": "uses_example", "offset_x": 12, "offset_y": -6}
        )
        application.execute(
            diagram, "set_relationship_label_offset", {"id": "uses_example", "offset_x": 0, "offset_y": 0}
        )
        assert "UpdateRelStyle" not in application.render(diagram)

    def test_rejects_an_unknown_relationship_when_setting_offsets(self) -> None:
        application, diagram = self._diagram_with_relationship()
        before = json.dumps(application.snapshot(diagram).to_dict(), sort_keys=True, separators=(",", ":"))
        with pytest.raises(RuntimeError, match=r"Relation 'missing_example' does not exist"):
            application.execute(
                diagram, "set_relationship_label_offset", {"id": "missing_example", "offset_x": 12, "offset_y": 8}
            )
        assert json.dumps(application.snapshot(diagram).to_dict(), sort_keys=True, separators=(",", ":")) == before
