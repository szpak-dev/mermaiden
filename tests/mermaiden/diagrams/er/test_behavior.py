import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestEntityRelationshipDiagram:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")

        for command in (
            DiagramCommand("configure", {"layoutDirection": "LR", "entityPadding": 20}),
            DiagramCommand("set_direction", {"direction": "LR"}),
            DiagramCommand("add_entity", {"id": "CUSTOMER", "label": 'Customer "account"'}),
            DiagramCommand(
                "add_attribute",
                {
                    "id": "customer_id",
                    "label": "id",
                    "data_type": "int",
                    "entity_id": "CUSTOMER",
                    "keys": ["PK"],
                    "comment": "identifier",
                },
            ),
            DiagramCommand("add_entity", {"id": "ORDER", "label": "Order"}),
            DiagramCommand(
                "add_relationship",
                {
                    "id": "places",
                    "source_id": "CUSTOMER",
                    "target_id": "ORDER",
                    "label": 'references content; "protected" — while scoped: [v2] #1 & <trusted>',
                    "notation": "||--o{",
                },
            ),
        ):
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("erDiagram").commands) == {
            "configure",
            "set_direction",
            "add_entity",
            "add_attribute",
            "add_relationship",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert "direction LR" in source
        assert "int id PK" in source
        assert (
            'CUSTOMER ||--o{ ORDER : "references content; #quot;protected#quot; — while scoped: '
            '[v2] #35;1 #38; #60;trusted#62;"'
        ) in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_entities(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.apply(diagram, DiagramCommand("add_entity", {"id": "ONE", "label": "One"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"entityPadding": "wide"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_entity", {"id": "ONE", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand("add_attribute", {"id": "x", "label": "x", "data_type": "int", "entity_id": "MISSING"}),
            )
