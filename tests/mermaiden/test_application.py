import json
from collections.abc import Mapping
from typing import Any, cast

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand
from mermaiden.runtime.snapshot import SnapshotError


class TestApplication:
    def _contains_none(self, value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, Mapping):
            return any(
                self._contains_none(item) for item in cast(Mapping[object, object], value).values()
            )
        if isinstance(value, list | tuple):
            return any(
                self._contains_none(item)
                for item in cast(list[object] | tuple[object, ...], value)
            )
        return False

    def test_creates_mutates_persists_restores_and_renders_a_diagram(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")

        application.apply(diagram, DiagramCommand("add_participant", {"id": "client", "label": "Client"}))
        application.apply(diagram, DiagramCommand("add_participant", {"id": "api", "label": "API"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_message",
                {"id": "request", "source_id": "client", "target_id": "api", "label": "Request"},
            ),
        )

        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(json.loads(json.dumps(payload)))

        assert application.render(restored) == application.render(diagram)
        assert restored.kind == "sequenceDiagram"

    def test_coerces_json_enum_command_arguments(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")

        application.apply(
            diagram,
            DiagramCommand("add_participant", {"id": "actor", "label": "Actor", "kind": "actor"}),
        )

        assert "actor actor as Actor" in application.render(diagram)

    def test_preserves_and_renders_a_class_identifier_separately_from_its_label(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")

        application.apply(
            diagram,
            DiagramCommand("add_class", {"id": "example_class", "label": "Example Class"}),
        )

        snapshot = application.snapshot(diagram)
        fields = cast(Mapping[str, object], snapshot.elements[0]["fields"])

        assert fields["id"] == "example_class"
        assert fields["label"] == "Example Class"
        assert 'class example_class["Example Class"] {' in application.render(diagram)

    def test_replaces_the_complete_configuration_using_concrete_defaults(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")

        application.apply(diagram, DiagramCommand("configure", {"padding": 12}))
        assert cast(Any, diagram.configuration).padding == 12

        application.apply(diagram, DiagramCommand("configure", {}))

        assert cast(Any, diagram.configuration).padding == 8
        assert 'block: {"padding": 8}' in application.render(diagram)

    def test_rejects_unknown_configuration_fields(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")

        with pytest.raises(UnknownCommand, match="'configure' has invalid arguments"):
            application.apply(diagram, DiagramCommand("configure", {"paddding": 12}))

    @pytest.mark.parametrize(
        ("diagram_id", "configuration"),
        (
            ("block", {"padding": 12}),
            ("pie", {"legendPosition": "top"}),
            ("gitGraph", {"nodeLabel": {"width": 90, "height": 110, "x": -20, "y": 5}}),
        ),
    )
    def test_persists_scalar_enum_and_nested_configurations(
        self,
        diagram_id: str,
        configuration: Mapping[str, object],
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram(diagram_id)
        application.apply(diagram, DiagramCommand("configure", configuration))
        source = application.render(diagram)

        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(json.loads(json.dumps(payload)))

        assert payload["version"] == 2
        assert "configuration" not in cast(Mapping[str, object], payload["properties"])
        assert not self._contains_none(payload["configuration"])
        assert restored.configuration == diagram.configuration
        assert type(restored.configuration) is type(diagram.configuration)
        assert application.render(restored) == source

    def test_rejects_version_one_before_reading_version_two_configuration(self) -> None:
        application = Application.create()
        payload = application.snapshot(application.create_diagram("block")).to_dict()
        payload["version"] = 1
        del payload["configuration"]

        with pytest.raises(SnapshotError, match="version '1'; expected version '2'"):
            application.restore(payload)
