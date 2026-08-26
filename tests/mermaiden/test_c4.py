import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand
from mermaiden.diagrams.c4.relations import Relationship, RelationshipDirection


class TestC4:
    @pytest.mark.parametrize(
        ("direction", "mermaid_function"),
        (
            (RelationshipDirection.DEFAULT, "Rel"),
            (RelationshipDirection.RIGHT, "Rel_R"),
            (RelationshipDirection.LEFT, "Rel_L"),
            (RelationshipDirection.UP, "Rel_Up"),
            (RelationshipDirection.DOWN, "Rel_Down"),
        ),
    )
    def test_renders_and_restores_every_relationship_direction(
        self,
        direction: RelationshipDirection,
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
                    "direction": direction.value,
                },
            ),
        )

        relationship = diagram.find_relations()[0]
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        restored_relationship = restored.find_relations()[0]

        assert isinstance(relationship, Relationship)
        assert relationship.direction is direction
        assert f'{mermaid_function}(user, app, "Uses")' in source
        assert isinstance(restored_relationship, Relationship)
        assert restored_relationship == relationship
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
