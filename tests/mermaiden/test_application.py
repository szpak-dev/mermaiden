import json
from collections.abc import Mapping
from typing import cast

from mermaiden.application import Application, DiagramCommand


class TestApplication:
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
