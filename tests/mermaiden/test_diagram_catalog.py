from mermaiden.application import Application


class TestDiagramCatalog:
    def test_discovers_pydantic_models_and_command_payloads_from_a_diagram_type(self) -> None:
        application = Application.create()

        description = application.diagram_description("sequenceDiagram")
        payload = application.command_payload("sequenceDiagram", "add_participant")

        assert set(description.elements) == {"participant", "participant_box"}
        assert {"message", "participant_event", "control", "directive"} == set(description.relations)
        assert "add_participant" in description.commands
        assert payload.model_validate({"id": "api", "kind": "actor"}).kind.value == "actor"

    def test_discovers_variadic_command_arguments_as_json_arrays(self) -> None:
        schema = Application.create().command_payload("sequenceDiagram", "add_note").model_json_schema()

        assert schema["properties"]["participant_ids"]["type"] == "array"
