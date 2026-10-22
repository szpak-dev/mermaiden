import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import cast

import pytest

from mermaiden import Application


class TestApplication:
    def _contains_none(self, value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, Mapping):
            return any(self._contains_none(item) for item in cast(Mapping[object, object], value).values())
        if isinstance(value, list | tuple):
            return any(self._contains_none(item) for item in cast(list[object] | tuple[object, ...], value))
        return False

    def test_creates_mutates_persists_restores_and_renders_a_diagram(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(diagram, "add_participant", {"id": "client_example", "label": "Client"})
        application.execute(diagram, "add_participant", {"id": "api_example", "label": "API"})
        application.execute(
            diagram,
            "add_message",
            {"id": "request_example", "source_id": "client_example", "target_id": "api_example", "label": "Request"},
        )
        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(json.loads(json.dumps(payload)))
        assert application.render(restored) == application.render(diagram)
        assert application.render(restored).endswith(
            'sequenceDiagram\nparticipant client_example@{ "type": "participant" } as Client\n'
            'participant api_example@{ "type": "participant" } as API\n'
            "client_example->>api_example: Request\n"
        )

    def test_creates_independent_diagram_instances_of_the_same_kind(self) -> None:
        application = Application.create()
        first = application.create_diagram("sequenceDiagram")
        second = application.create_diagram("sequenceDiagram")
        application.execute(first, "add_participant", {"id": "first_example", "label": "First"})
        assert first is not second
        assert "participant first_example" in application.render(first)
        assert application.snapshot(second).to_dict()["elements"] == []

    def test_reuses_catalog_metadata_across_applications(self) -> None:
        with Application.create() as first, Application.create() as second:
            assert first.diagram_description("sequenceDiagram") is second.diagram_description("sequenceDiagram")
            assert first.command_payload("sequenceDiagram", "add_message") is second.command_payload(
                "sequenceDiagram", "add_message"
            )

    def test_exposes_the_complete_snapshot_contract_identity(self) -> None:
        with Application.create() as application:
            identity = application.snapshot_contract_identity("sequenceDiagram")
        assert identity.kind == "sequenceDiagram"
        assert identity.snapshot_version == 9
        assert identity.registry_fingerprint == "0553d6e63d06ded7322dc5db4bccb97d6ba7cb1ffa36b2d288a9b5c782dd5f1c"

    def test_returns_the_same_snapshot_contract_identity_across_applications(self) -> None:
        with Application.create() as first, Application.create() as second:
            assert first.snapshot_contract_identity("sequenceDiagram") == second.snapshot_contract_identity(
                "sequenceDiagram"
            )

    def test_exposes_snapshot_contract_identity_for_every_advertised_diagram(self) -> None:
        with Application.create() as application:
            advertised = application.available_diagrams()
            identities = tuple(application.snapshot_contract_identity(info.id) for info in advertised)
        assert tuple(identity.kind for identity in identities) == tuple(info.id for info in advertised)
        assert {identity.snapshot_version for identity in identities} == {9}
        assert {identity.registry_fingerprint for identity in identities} == {
            "0553d6e63d06ded7322dc5db4bccb97d6ba7cb1ffa36b2d288a9b5c782dd5f1c"
        }

    def test_rejects_snapshot_contract_identity_for_an_unknown_diagram(self) -> None:
        with (
            Application.create() as application,
            pytest.raises(RuntimeError, match=r"Snapshot diagram kind 'unknown' is not registered"),
        ):
            application.snapshot_contract_identity("unknown")

    def test_keeps_diagram_state_isolated_between_applications(self) -> None:
        with Application.create() as first, Application.create() as second:
            first_diagram = first.create_diagram("sequenceDiagram")
            second_diagram = second.create_diagram("sequenceDiagram")
            first.execute(first_diagram, "add_participant", {"id": "first_example", "label": "First"})
            assert first_diagram is not second_diagram
            assert second.snapshot(second_diagram).to_dict()["elements"] == []

    def test_rejects_every_operation_after_close_and_keeps_close_idempotent(self, tmp_path: Path) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.execute(diagram, "add_block", {"id": "example", "label": "Example"})
        snapshot = application.snapshot(diagram).to_dict()
        operations: tuple[Callable[[], object], ...] = (
            application.available_diagrams,
            lambda: application.diagram_info("block"),
            lambda: application.diagram_description("block"),
            lambda: application.command_payload("block", "add_block"),
            lambda: application.snapshot_contract_identity("block"),
            lambda: application.create_diagram("block"),
            lambda: application.apply_batch(diagram, ()),
            lambda: application.execute(diagram, "configure", {}),
            lambda: application.snapshot(diagram),
            lambda: application.restore(snapshot),
            lambda: application.render(diagram),
            lambda: application.validate_render(diagram),
            lambda: application.mermaid_version,
            lambda: application.mermaid_cli_version,
            lambda: application.write_preview({"block": "block\n"}, tmp_path / "preview.html"),
            application.__enter__,
        )
        application.close()
        application.close()
        for operation in operations:
            with pytest.raises(RuntimeError, match=r"Application is closed"):
                operation()
        assert not (tmp_path / "preview.html").exists()

    def test_rejects_an_unknown_direct_command_without_mutation_and_recovers(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"Command 'missing_example' is not supported"):
            application.execute(diagram, "missing_example", {})
        assert application.snapshot(diagram).to_dict() == before
        application.execute(diagram, "add_block", {"id": "recovery_example", "label": "Recovery"})
        assert 'recovery_example["Recovery"]' in application.render(diagram)

    def test_coerces_json_enum_command_arguments(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(diagram, "add_participant", {"id": "actor_example", "label": "Actor", "kind": "actor"})
        assert "actor actor_example as Actor" in application.render(diagram)

    def test_preserves_and_renders_a_class_identifier_separately_from_its_label(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "example_class", "label": "Example Class"})
        snapshot = application.snapshot(diagram).to_dict()
        element = cast(Mapping[str, object], cast(list[object], snapshot["elements"])[0])
        fields = cast(Mapping[str, object], element["fields"])
        assert fields["id"] == "example_class"
        assert fields["label"] == "Example Class"
        assert 'class c_v_example_class["Example Class"] {' in application.render(diagram)

    def test_replaces_the_complete_configuration_using_concrete_defaults(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.execute(diagram, "configure", {"padding": 12})
        application.execute(diagram, "add_block", {"id": "example", "label": "Example"})
        assert 'block: {"useMaxWidth": true, "padding": 12.0}' in application.render(diagram)
        application.execute(diagram, "configure", {})
        assert 'block: {"useMaxWidth": true, "padding": 8.0}' in application.render(diagram)

    def test_rejects_unknown_configuration_fields(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        with pytest.raises(RuntimeError, match=r"'configure' has invalid arguments"):
            application.execute(diagram, "configure", {"paddding": 12})

    @pytest.mark.parametrize(
        ("diagram_id", "configuration", "setup"),
        (
            ("block", {"padding": 12, "useWidth": 640}, ("add_block", {"id": "example", "label": "Example"})),
            (
                "architecture-beta",
                {"nodeSeparation": 96, "seed": 7},
                ("add_service", {"id": "example", "label": "Example"}),
            ),
            (
                "C4Context",
                {"c4ShapeInRow": 3, "messageFontSize": 16},
                ("add_person", {"id": "example", "label": "Example"}),
            ),
            ("pie", {"legendPosition": "top"}, ("add_slice", {"id": "example", "label": "Example", "value": 1})),
            (
                "gitGraph",
                {"nodeLabel": {"width": 90, "height": 110, "x": -20, "y": 5}},
                ("add_commit", {"id": "example", "label": "Example"}),
            ),
        ),
    )
    def test_persists_scalar_enum_and_nested_configurations(
        self, diagram_id: str, configuration: Mapping[str, object], setup: tuple[str, Mapping[str, object]]
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram(diagram_id)
        application.execute(diagram, "configure", configuration)
        application.execute(diagram, *setup)
        source = application.render(diagram)
        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(json.loads(json.dumps(payload)))
        assert payload["version"] == 9
        assert "configuration" not in cast(Mapping[str, object], payload["properties"])
        assert not self._contains_none(payload["configuration"])
        assert application.snapshot(restored).to_dict() == payload
        assert application.render(restored) == source

    def test_serializes_non_default_architecture_configuration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.execute(
            diagram,
            "configure",
            {
                "useMaxWidth": False,
                "padding": 48,
                "iconSize": 96,
                "fontSize": 18,
                "randomize": True,
                "nodeSeparation": 120,
                "idealEdgeLengthMultiplier": 2,
                "edgeElasticity": 0.7,
                "numIter": 3000,
                "seed": 7,
            },
        )
        application.execute(diagram, "add_service", {"id": "example", "label": "Example"})
        expected = (
            'architecture: {"useMaxWidth": false, "padding": 48.0, "iconSize": 96.0, "fontSize": 18.0, '
            '"randomize": true, "nodeSeparation": 120.0, "idealEdgeLengthMultiplier": 2.0, '
            '"edgeElasticity": 0.7, "numIter": 3000.0, "seed": 7.0}'
        )
        assert expected in application.render(diagram)

    def test_serializes_non_default_c4_configuration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("C4Context")
        application.execute(
            diagram,
            "configure",
            {
                "diagramMarginX": 64,
                "diagramMarginY": 24,
                "c4ShapeMargin": 56,
                "c4ShapePadding": 28,
                "width": 240,
                "height": 72,
                "boxMargin": 16,
                "useMaxWidth": False,
                "c4ShapeInRow": 3,
                "nextLinePaddingX": 12,
                "c4BoundaryInRow": 1,
                "messageFontSize": 16,
            },
        )
        application.execute(diagram, "add_person", {"id": "example", "label": "Example"})
        source = application.render(diagram)
        for expected in (
            '"useMaxWidth": false',
            '"diagramMarginX": 64',
            '"diagramMarginY": 24',
            '"c4ShapeMargin": 56',
            '"c4ShapePadding": 28',
            '"width": 240',
            '"height": 72',
            '"boxMargin": 16',
            '"c4ShapeInRow": 3',
            '"nextLinePaddingX": 12.0',
            '"c4BoundaryInRow": 1',
            '"messageFontSize": 16.0',
        ):
            assert expected in source
