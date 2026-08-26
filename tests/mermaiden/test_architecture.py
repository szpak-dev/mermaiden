import json

from mermaiden.application import Application, DiagramCommand
from mermaiden.diagrams.architecture.relations import Edge


class TestArchitecture:
    def test_renders_and_restores_a_quoted_edge_label(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.apply(diagram, DiagramCommand("add_service", {"id": "client", "label": "Client"}))
        application.apply(diagram, DiagramCommand("add_service", {"id": "api", "label": "API"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_edge",
                {
                    "id": "client_api",
                    "source_id": "client",
                    "target_id": "api",
                    "label": 'HTTPS "mTLS"',
                },
            ),
        )

        edge = diagram.find_relations()[0]
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        restored_edge = restored.find_relations()[0]

        assert isinstance(edge, Edge)
        assert edge.label == 'HTTPS "mTLS"'
        assert 'client:R -["HTTPS \\"mTLS\\""]-> L:api' in source
        assert isinstance(restored_edge, Edge)
        assert restored_edge == edge
        assert application.render(restored) == source

    def test_keeps_an_empty_edge_label_compact(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.apply(diagram, DiagramCommand("add_service", {"id": "client", "label": "Client"}))
        application.apply(diagram, DiagramCommand("add_service", {"id": "api", "label": "API"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_edge",
                {"id": "client_api", "source_id": "client", "target_id": "api"},
            ),
        )

        assert "client:R --> L:api" in application.render(diagram)
