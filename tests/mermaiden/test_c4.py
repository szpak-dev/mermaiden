import json
from typing import Any

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestC4:
    def _diagram_with_relationship(self) -> tuple[Application, Any]:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.apply(diagram, DiagramCommand("add_person", {"id": "user", "label": "User"}))
        application.apply(diagram, DiagramCommand("add_system", {"id": "app", "label": "Application"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_relationship",
                {"id": "uses", "source_id": "user", "target_id": "app", "label": "Uses"},
            ),
        )
        return application, diagram

    @pytest.mark.parametrize(
        ("direction", "mermaid_function"),
        (
            ("Rel", "Rel"),
            ("Rel_R", "Rel_R"),
            ("Rel_L", "Rel_L"),
            ("Rel_Up", "Rel_Up"),
            ("Rel_Down", "Rel_Down"),
        ),
    )
    def test_renders_and_restores_every_relationship_direction(
        self,
        direction: str,
        mermaid_function: str,
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.apply(diagram, DiagramCommand("add_person", {"id": "user", "label": "User"}))
        application.apply(diagram, DiagramCommand("add_system", {"id": "app", "label": "Application"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_relationship",
                {
                    "id": "uses",
                    "source_id": "user",
                    "target_id": "app",
                    "label": "Uses",
                    "direction": direction,
                },
            ),
        )

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert f'{mermaid_function}(user, app, "Uses")' in source
        assert application.render(restored) == source

    def test_rejects_an_unknown_relationship_direction(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")

        with pytest.raises(UnknownCommand, match="'add_relationship' has invalid arguments"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_relationship",
                    {
                        "id": "uses",
                        "source_id": "user",
                        "target_id": "app",
                        "label": "Uses",
                        "direction": "Rel_Sideways",
                    },
                ),
            )

    @pytest.mark.parametrize(
        ("offset_x", "offset_y"),
        (
            (16, 8),
            (-16, -8),
            (-16, 8),
        ),
    )
    def test_renders_and_restores_relationship_label_offsets(self, offset_x: int, offset_y: int) -> None:
        application, diagram = self._diagram_with_relationship()
        application.apply(
            diagram,
            DiagramCommand(
                "set_relationship_label_offset",
                {"id": "uses", "offset_x": offset_x, "offset_y": offset_y},
            ),
        )

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert f'UpdateRelStyle(user, app, $offsetX="{offset_x}", $offsetY="{offset_y}")' in source
        assert application.render(restored) == source

    def test_renders_offsets_after_every_relationship_declaration(self) -> None:
        application, diagram = self._diagram_with_relationship()
        application.apply(diagram, DiagramCommand("add_system", {"id": "database", "label": "Database"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_relationship",
                {"id": "reads", "source_id": "app", "target_id": "database", "label": "Reads"},
            ),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "set_relationship_label_offset",
                {"id": "uses", "offset_x": 12, "offset_y": -6},
            ),
        )

        source = application.render(diagram)

        assert source.index('Rel(app, database, "Reads")') < source.index("UpdateRelStyle(user, app")

    def test_resetting_both_offsets_removes_the_style_statement(self) -> None:
        application, diagram = self._diagram_with_relationship()
        application.apply(
            diagram,
            DiagramCommand(
                "set_relationship_label_offset",
                {"id": "uses", "offset_x": 12, "offset_y": -6},
            ),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "set_relationship_label_offset",
                {"id": "uses", "offset_x": 0, "offset_y": 0},
            ),
        )

        assert "UpdateRelStyle" not in application.render(diagram)

    def test_rejects_an_unknown_relationship_when_setting_offsets(self) -> None:
        application, diagram = self._diagram_with_relationship()

        with pytest.raises(RuntimeError, match="Relationship 'missing' does not exist"):
            application.apply(
                diagram,
                DiagramCommand(
                    "set_relationship_label_offset",
                    {"id": "missing", "offset_x": 12, "offset_y": 8},
                ),
            )
