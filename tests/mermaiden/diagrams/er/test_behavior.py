import json
import re
from collections.abc import Mapping
from typing import cast

import pytest

from mermaiden import Application


class TestEntityRelationshipDiagram:
    @pytest.mark.parametrize(
        "command",
        (("configure", {"layoutDirection": "LR"}), ("set_direction", {"direction": "LR"})),
        ids=("configure", "set_direction"),
    )
    def test_direction_commands_keep_configuration_body_and_restored_snapshot_in_sync(
        self, command: tuple[str, Mapping[str, object]]
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "CUSTOMER_example", "label": "Customer"})
        application.execute(diagram, *command)
        source = application.render(diagram)
        snapshot = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        restored = application.restore(snapshot)
        assert '"layoutDirection": "LR"' in source
        assert "\nerDiagram\ndirection LR\n" in source
        assert snapshot["configuration"]["fields"]["layout_direction"] == "LR"
        assert snapshot["properties"]["direction"] == "LR"
        assert application.render(restored) == source
        assert application.snapshot(restored).to_dict() == snapshot

    @pytest.mark.parametrize(
        ("operation", "arguments", "field"),
        (
            ("configure", {"layoutDirection": "SIDEWAYS"}, "layoutDirection"),
            ("set_direction", {"direction": "SIDEWAYS"}, "direction"),
        ),
    )
    def test_direction_commands_advertise_and_enforce_supported_values(
        self, operation: str, arguments: dict[str, object], field: str
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        schema = application.diagram_description("erDiagram").commands[operation]
        properties = cast(dict[str, dict[str, object]], schema["properties"])
        definitions = cast(dict[str, dict[str, object]], schema["$defs"])
        assert properties[field]["$ref"] == "#/$defs/EntityRelationshipDirection"
        assert definitions["EntityRelationshipDirection"]["enum"] == ["TB", "BT", "LR", "RL"]
        with pytest.raises(RuntimeError, match=f"'{operation}' has invalid arguments"):
            application.execute(diagram, operation, arguments)

    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        for command in (
            ("configure", {"layoutDirection": "LR", "entityPadding": 20}),
            ("set_direction", {"direction": "LR"}),
            ("add_entity", {"id": "CUSTOMER_example", "label": 'Customer "account"'}),
            (
                "add_attribute",
                {
                    "id": "customer_id_example",
                    "label": "id",
                    "data_type": "int",
                    "entity_id": "CUSTOMER_example",
                    "keys": ["PK"],
                    "comment": "identifier",
                },
            ),
            ("add_entity", {"id": "ORDER_example", "label": "Order"}),
            (
                "add_relationship",
                {
                    "id": "places_example",
                    "source_id": "CUSTOMER_example",
                    "target_id": "ORDER_example",
                    "label": 'references content; "protected" — while scoped: [v2] #1 & <trusted>',
                    "source_cardinality": "exactly_one",
                    "target_cardinality": "zero_or_more",
                    "identifying": True,
                },
            ),
        ):
            application.execute(diagram, *command)
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
        expected_relation = (
            'e_v_CUSTOMER_example ||--o{ e_v_ORDER_example : "references content; '
            '#quot;protected#quot; — while scoped: [v2] #35;1 #38; #60;trusted#62;"'
        )
        assert expected_relation in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_entities(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "ONE_example", "label": "One"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"entityPadding": "wide"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_relationship",
                {
                    "id": "syntax_example",
                    "source_id": "ONE_example",
                    "target_id": "ONE_example",
                    "label": "syntax_example",
                    "notation": "||--||",
                },
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_entity", {"id": "ONE_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_attribute",
                {"id": "x_example", "label": "x_example", "data_type": "int", "entity_id": "MISSING_example"},
            )

    @pytest.mark.parametrize("data_type", ("positive int", "", "0int", "PK", "PK-type", "int??", "int\n"))
    def test_rejects_unrenderable_attribute_types_before_changing_the_snapshot(self, data_type: str) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "CUSTOMER_example", "label": "Customer"})
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"invalid arguments"):
            application.execute(
                diagram,
                "add_attribute",
                {
                    "id": "revision_example",
                    "label": "revision_example",
                    "data_type": data_type,
                    "entity_id": "CUSTOMER_example",
                },
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_an_unrenderable_attribute_type_update_without_changing_the_snapshot(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "CUSTOMER_example", "label": "Customer"})
        application.execute(
            diagram,
            "add_attribute",
            {
                "id": "revision_example",
                "label": "revision_example",
                "data_type": "int",
                "entity_id": "CUSTOMER_example",
            },
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"invalid arguments"):
            application.execute(
                diagram,
                "update_element",
                {"id": "revision_example", "kind": "entity_attribute", "changes": {"data_type": "positive int"}},
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_a_persisted_unrenderable_attribute_type(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        application.execute(diagram, "add_entity", {"id": "CUSTOMER_example", "label": "Customer"})
        application.execute(
            diagram,
            "add_attribute",
            {
                "id": "revision_example",
                "label": "revision_example",
                "data_type": "int",
                "entity_id": "CUSTOMER_example",
            },
        )
        payload = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        entity = cast(dict[str, object], cast(list[object], payload["elements"])[0])
        entity_fields = cast(dict[str, object], entity["fields"])
        attribute = cast(dict[str, object], cast(list[object], entity_fields["elements"])[0])
        cast(dict[str, object], attribute["fields"])["data_type"] = "positive int"
        with pytest.raises(ValueError, match=r"data_type"):
            application.restore(payload)

    def test_publishes_the_same_attribute_type_restriction_for_add_update_and_persistence(self) -> None:
        application = Application.create()
        add_schema = application.command_payload("erDiagram", "add_attribute").schema()
        update_schema = application.command_payload("erDiagram", "update_element").schema()
        object_schema = application.diagram_description("erDiagram").elements["entity_attribute"]
        add_properties = cast(Mapping[str, Mapping[str, object]], add_schema["properties"])
        add_definitions = cast(Mapping[str, Mapping[str, object]], add_schema["$defs"])
        update_definitions = cast(Mapping[str, Mapping[str, object]], update_schema["$defs"])
        add_type = add_properties["data_type"]
        update_changes = update_definitions["EntityRelationshipDiagram_update_element_entity_attribute_changes"]
        update_properties = cast(Mapping[str, Mapping[str, object]], update_changes["properties"])
        update_type = update_properties["data_type"]
        object_type = cast(Mapping[str, Mapping[str, object]], object_schema["properties"])["data_type"]
        reference = cast(str, add_type["$ref"]).removeprefix("#/$defs/")
        pattern = cast(str, add_definitions[reference]["pattern"])
        assert pattern == update_type["pattern"] == object_type["pattern"]
        assert re.search(pattern, "public.geometry(point,4326)?")
        assert re.search(pattern, "positive~ int ~")
        assert re.search(pattern, "`positive int`")
        assert not re.search(pattern, "positive int")
