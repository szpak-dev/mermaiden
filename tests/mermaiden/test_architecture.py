import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand
from mermaiden.core.constraint import ChangeRejected
from mermaiden.diagrams.architecture.diagram import Architecture
from mermaiden.diagrams.architecture.relations import Alignment, AlignmentAxis, Edge


class TestArchitecture:
    def _diagram_with_alignment_members(self) -> tuple[Application, Architecture]:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        assert isinstance(diagram, Architecture)
        application.apply(diagram, DiagramCommand("add_service", {"id": "client", "label": "Client"}))
        application.apply(diagram, DiagramCommand("add_junction", {"id": "gateway", "label": "Gateway"}))
        application.apply(diagram, DiagramCommand("add_service", {"id": "api", "label": "API"}))
        return application, diagram

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

    @pytest.mark.parametrize(
        ("axis", "directive"),
        (
            (AlignmentAxis.ROW, "align row client gateway api"),
            (AlignmentAxis.COLUMN, "align column client gateway api"),
        ),
    )
    def test_renders_and_restores_an_ordered_alignment(
        self,
        axis: AlignmentAxis,
        directive: str,
    ) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "primary", "axis": axis.value, "member_ids": ["client", "gateway", "api"]},
            ),
        )

        alignment = diagram.find_relations()[0]
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        restored_alignment = restored.find_relations()[0]

        assert isinstance(alignment, Alignment)
        assert alignment.id == "primary"
        assert alignment.axis is axis
        assert alignment.member_ids == ("client", "gateway", "api")
        assert directive in source
        assert source.index("service api") < source.index(directive)
        assert isinstance(restored_alignment, Alignment)
        assert restored_alignment == alignment
        assert application.render(restored) == source

    @pytest.mark.parametrize(
        ("member_ids", "message"),
        (
            (("client",), "requires at least two members"),
            (("client", "client"), "members must be unique"),
            (("client", "missing"), "references unknown member 'missing'"),
        ),
    )
    def test_rejects_invalid_alignment_members(self, member_ids: tuple[str, ...], message: str) -> None:
        application, diagram = self._diagram_with_alignment_members()

        with pytest.raises(ChangeRejected, match=message):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "invalid", "axis": "row", "member_ids": member_ids},
                ),
            )

    def test_rejects_groups_as_alignment_members(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(diagram, DiagramCommand("add_group", {"id": "platform", "label": "Platform"}))

        with pytest.raises(ChangeRejected, match="member 'platform' must be a service or junction"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "invalid", "axis": "column", "member_ids": ("client", "platform")},
                ),
            )

    def test_rejects_an_unknown_alignment_axis(self) -> None:
        application, diagram = self._diagram_with_alignment_members()

        with pytest.raises(UnknownCommand, match="'add_alignment' has invalid arguments"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "invalid", "axis": "diagonal", "member_ids": ("client", "gateway")},
                ),
            )

    def test_rejects_duplicate_alignment_ids(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        command = DiagramCommand(
            "add_alignment",
            {"id": "primary", "axis": "row", "member_ids": ("client", "gateway")},
        )
        application.apply(diagram, command)

        with pytest.raises(ChangeRejected, match="Relation 'primary' already exists"):
            application.apply(diagram, command)
