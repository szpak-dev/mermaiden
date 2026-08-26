import json
from collections.abc import Mapping
from typing import Any, cast

import pytest
from pydantic import ValidationError

from mermaiden.application import Application, DiagramCommand
from mermaiden.diagrams.block.configuration import BlockDiagramConfiguration
from mermaiden.diagrams.configuration import MermaidDiagramConfiguration
from mermaiden.diagrams.gitgraph.configuration import GitGraphDiagramConfiguration
from mermaiden.diagrams.requirement.configuration import RequirementDiagramConfiguration


class TestMermaidConfiguration:
    def _contains_json_null(self, value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, Mapping):
            mapping = cast(Mapping[object, object], value)
            return mapping.get("type") == "null" or any(
                self._contains_json_null(item) for item in mapping.values()
            )
        if isinstance(value, list | tuple):
            return any(
                self._contains_json_null(item)
                for item in cast(list[object] | tuple[object, ...], value)
            )
        return False

    def test_diagram_configuration_provides_a_source_keyed_mermaid_document(self) -> None:
        configuration = BlockDiagramConfiguration(padding=12)

        assert configuration.document("block").to_mermaid() == {
            "wrap": True,
            "block": {"padding": 12},
        }

    def test_diagram_configuration_validates_its_values(self) -> None:
        with pytest.raises(ValidationError):
            BlockDiagramConfiguration(padding=cast(Any, "invalid"))

        with pytest.raises(ValidationError):
            BlockDiagramConfiguration.model_validate({"paddding": 12})

    def test_configuration_serialization_converts_nested_keys_to_camel_case(self) -> None:
        document = cast(
            dict[str, dict[str, object]], GitGraphDiagramConfiguration().document("gitGraph").to_mermaid()
        )
        assert document["gitGraph"]["nodeLabel"] == {
            "width": 75,
            "height": 100,
            "x": -25,
            "y": 0,
        }
        requirement = cast(
            dict[str, dict[str, object]], RequirementDiagramConfiguration().document("requirement").to_mermaid()
        )

        assert requirement["requirement"]["rectFill"] == "#f9f9f9"

    def test_every_diagram_exposes_a_strict_non_nullable_configuration_command(self) -> None:
        application = Application.create()

        for info in application.available_diagrams():
            diagram = application.create_diagram(info.id)
            payload_type = application.command_payload(info.id, "configure")
            schema = payload_type.model_json_schema()
            configuration = payload_type.model_validate({})

            assert payload_type is type(diagram.configuration)
            assert issubclass(payload_type, MermaidDiagramConfiguration)
            assert application.diagram_description(info.id).commands["configure"] == schema
            assert schema["additionalProperties"] is False
            assert not self._contains_json_null(schema)
            assert not self._contains_json_null(configuration.model_dump(mode="json", by_alias=True))
            assert not self._contains_json_null(diagram.mermaid_configuration)
            with pytest.raises(ValidationError):
                payload_type.model_validate({"unknown_configuration_field": True})

            application.apply(diagram, DiagramCommand("configure", {}))
            source = application.render(diagram)
            snapshot = application.snapshot(diagram).to_dict()
            restored = application.restore(json.loads(json.dumps(snapshot)))

            assert not self._contains_json_null(snapshot["configuration"])
            assert restored.configuration == configuration
            assert type(restored.configuration) is payload_type
            assert application.render(restored) == source
