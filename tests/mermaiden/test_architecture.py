import json
from typing import Any

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestArchitecture:
    def _diagram_with_alignment_members(self) -> tuple[Application, Any]:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.apply(diagram, DiagramCommand("add_service", {"id": "client", "label": "Client"}))
        application.apply(diagram, DiagramCommand("add_junction", {"id": "gateway", "label": "Gateway"}))
        application.apply(diagram, DiagramCommand("add_service", {"id": "api", "label": "API"}))
        return application, diagram

    def _diagram_with_group(self, columns: int, *member_ids: str) -> tuple[Application, Any]:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.apply(
            diagram,
            DiagramCommand("add_group", {"id": "platform", "label": "Platform", "columns": columns}),
        )
        for member_id in member_ids:
            application.apply(
                diagram,
                DiagramCommand(
                    "add_service",
                    {"id": member_id, "label": member_id.upper(), "group_id": "platform"},
                ),
            )
        return application, diagram

    def _alignment_directives(self, application: Application, diagram: Any) -> list[str]:
        return [
            line.strip()
            for line in application.render(diagram).splitlines()
            if line.strip().startswith("align ")
        ]

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

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert 'client:R -["HTTPS \\"mTLS\\""]-> L:api' in source
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
            ("row", "align row client gateway api"),
            ("column", "align column client gateway api"),
        ),
    )
    def test_renders_and_restores_an_ordered_alignment(
        self,
        axis: str,
        directive: str,
    ) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "primary", "axis": axis, "member_ids": ["client", "gateway", "api"]},
            ),
        )

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert directive in source
        assert source.index("service api") < source.index(directive)
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

        with pytest.raises(RuntimeError, match=message):
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

        with pytest.raises(RuntimeError, match="member 'platform' must be a service or junction"):
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

        with pytest.raises(RuntimeError, match="Relation 'primary' already exists"):
            application.apply(diagram, command)

    def test_derives_a_grid_from_direct_members_without_persisting_alignments(self) -> None:
        application, diagram = self._diagram_with_group(2, "a")
        application.apply(
            diagram,
            DiagramCommand(
                "add_group",
                {"id": "nested", "label": "Nested", "parent_id": "platform", "columns": 1},
            ),
        )
        for member_id in ("x", "y"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_service",
                    {"id": member_id, "label": member_id.upper(), "group_id": "nested"},
                ),
            )
        for member_id in ("b", "c", "d"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_junction",
                    {"id": member_id, "label": member_id.upper(), "group_id": "platform"},
                ),
            )

        snapshot = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(snapshot)))

        assert self._alignment_directives(application, diagram) == [
            "align column x y",
            "align row a b",
            "align row c d",
            "align column a c",
            "align column b d",
        ]
        assert "align row a nested" not in source
        assert "align column a x" not in source
        assert snapshot["relations"] == []
        assert application.render(restored) == source

    @pytest.mark.parametrize(
        ("columns", "member_ids", "directives"),
        (
            (1, ("a", "b", "c"), ["align column a b c"]),
            (2, ("a", "b", "c"), ["align row a b", "align column a c"]),
            (4, ("a", "b", "c"), ["align row a b c"]),
            (3, ("a",), []),
        ),
    )
    def test_columns_derive_deterministic_non_singleton_directives(
        self,
        columns: int,
        member_ids: tuple[str, ...],
        directives: list[str],
    ) -> None:
        application, diagram = self._diagram_with_group(columns, *member_ids)

        assert self._alignment_directives(application, diagram) == directives

    @pytest.mark.parametrize("columns", (0, -1))
    def test_rejects_non_positive_group_columns(self, columns: int) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")

        with pytest.raises(UnknownCommand, match="'add_group' has invalid arguments"):
            application.apply(
                diagram,
                DiagramCommand("add_group", {"id": "platform", "label": "Platform", "columns": columns}),
            )
