import pytest
from pydantic import ValidationError

from mermaiden.application import Application


class TestDiagramCatalog:
    def test_discovers_pydantic_models_and_command_payloads_from_a_diagram_type(self) -> None:
        application = Application.create()

        description = application.diagram_description("sequenceDiagram")
        payload = application.command_payload("sequenceDiagram", "add_participant")

        assert set(description.elements) == {"participant", "participant_box"}
        assert {"message", "participant_event", "control", "directive"} == set(description.relations)
        assert "add_participant" in description.commands
        validated = payload.model_validate({"id": "api", "label": "API", "kind": "actor"})
        assert validated.model_dump(mode="json")["kind"] == "actor"

    def test_discovers_each_diagrams_concrete_configuration_as_a_command_payload(self) -> None:
        application = Application.create()

        for info in application.available_diagrams():
            payload_type = application.command_payload(info.id, "configure")

            assert application.diagram_description(info.id).commands["configure"] == payload_type.model_json_schema()
            payload_type.model_validate({})

    @pytest.mark.parametrize(
        ("diagram_id", "command_name"),
        (
            ("classDiagram", "add_class"),
            ("sequenceDiagram", "add_participant"),
            ("stateDiagram-v2", "add_state"),
            ("stateDiagram-v2", "add_composite"),
        ),
    )
    def test_requires_human_facing_labels(self, diagram_id: str, command_name: str) -> None:
        application = Application.create()
        schema = application.command_payload(diagram_id, command_name).model_json_schema()

        assert "label" in schema["required"]

    @pytest.mark.parametrize(
        ("diagram_id", "command_name"),
        (
            ("stateDiagram-v2", "add_choice"),
            ("stateDiagram-v2", "add_fork"),
            ("stateDiagram-v2", "add_join"),
            ("stateDiagram-v2", "add_transition"),
            ("classDiagram", "add_relation"),
        ),
    )
    def test_keeps_symbolic_and_relation_labels_optional(self, diagram_id: str, command_name: str) -> None:
        schema = Application.create().command_payload(diagram_id, command_name).model_json_schema()

        assert "label" not in schema["required"]
        assert schema["properties"]["label"]["default"] == ""

    def test_requires_one_or_two_sequence_note_targets(self) -> None:
        payload = Application.create().command_payload("sequenceDiagram", "add_note")
        schema = payload.model_json_schema()
        targets = schema["properties"]["participant_ids"]

        assert "participant_ids" in schema["required"]
        assert targets["type"] == "array"
        assert targets["minItems"] == 1
        assert targets["maxItems"] == 2
        one_target = payload.model_validate({"id": "note", "text": "One", "participant_ids": ["api"]})

        assert one_target.model_dump(mode="json")["participant_ids"] == ["api"]
        two_targets = payload.model_validate(
            {"id": "note", "text": "Two", "participant_ids": ["api", "worker"]}
        )
        assert two_targets.model_dump(mode="json")["participant_ids"] == ["api", "worker"]
        for participant_ids in ([], ["api", "worker", "queue"]):
            with pytest.raises(ValidationError):
                payload.model_validate({"id": "note", "text": "Invalid", "participant_ids": participant_ids})
