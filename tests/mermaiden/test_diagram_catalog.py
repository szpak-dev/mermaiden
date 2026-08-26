from inspect import Parameter, signature
from typing import Any, cast

import pytest
from pydantic import ValidationError

from mermaiden.application import Application
from mermaiden.diagrams.sequence.diagram import SequenceDiagram


class TestDiagramCatalog:
    def test_discovers_pydantic_models_and_command_payloads_from_a_diagram_type(self) -> None:
        application = Application.create()

        description = application.diagram_description("sequenceDiagram")
        payload = application.command_payload("sequenceDiagram", "add_participant")

        assert set(description.elements) == {"participant", "participant_box"}
        assert {"message", "participant_event", "control", "directive"} == set(description.relations)
        assert "add_participant" in description.commands
        assert cast(Any, payload.model_validate({"id": "api", "label": "API", "kind": "actor"})).kind.value == "actor"

    def test_discovers_each_diagrams_concrete_configuration_as_a_command_payload(self) -> None:
        application = Application.create()

        for info in application.available_diagrams():
            diagram = application.create_diagram(info.id)
            payload_type = application.command_payload(info.id, "configure")

            assert payload_type is type(diagram.configuration)
            assert application.diagram_description(info.id).commands["configure"] == payload_type.model_json_schema()

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
        diagram_type = application.diagram_info(diagram_id).diagram_type
        schema = application.command_payload(diagram_id, command_name).model_json_schema()

        assert signature(getattr(diagram_type, command_name)).parameters["label"].default is Parameter.empty
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

        assert signature(SequenceDiagram.add_note).parameters["participant_ids"].kind is Parameter.VAR_POSITIONAL
        assert "participant_ids" in schema["required"]
        assert targets["type"] == "array"
        assert targets["minItems"] == 1
        assert targets["maxItems"] == 2
        one_target = payload.model_validate({"id": "note", "text": "One", "participant_ids": ["api"]})

        assert cast(Any, one_target).participant_ids == ("api",)
        assert cast(
            Any,
            payload.model_validate({"id": "note", "text": "Two", "participant_ids": ["api", "worker"]}),
        ).participant_ids == ("api", "worker")
        for participant_ids in ([], ["api", "worker", "queue"]):
            with pytest.raises(ValidationError):
                payload.model_validate({"id": "note", "text": "Invalid", "participant_ids": participant_ids})
