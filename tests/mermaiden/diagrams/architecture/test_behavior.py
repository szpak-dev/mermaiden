import json
from typing import Any

import pytest
from contracts.mutation_conformance import assert_mutation_conformance

from mermaiden.application import Application, DiagramCommand, UnknownCommand
from mermaiden.core import ChangeRejected


class TestArchitecture:
    def test_exercises_note_and_configuration_commands(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")

        application.apply(diagram, DiagramCommand("configure", {"nodeSeparation": 96, "seed": 7}))
        application.apply(diagram, DiagramCommand("add_group", {"id": "group_example", "label": "Group Example"}))
        application.apply(diagram, DiagramCommand("add_service", {"id": "client_example", "label": "Client Example"}))
        application.apply(
            diagram, DiagramCommand("add_junction", {"id": "gateway_example", "label": "Gateway Example"})
        )
        application.apply(diagram, DiagramCommand("add_service", {"id": "api_example", "label": "API Example"}))
        application.apply(
            diagram,
            DiagramCommand(
                "add_edge",
                {
                    "id": "edge_example",
                    "source_id": "client_example",
                    "target_id": "api_example",
                    "label": "HTTPS Example",
                },
            ),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {
                    "id": "alignment_example",
                    "axis": "row",
                    "member_ids": ["client_example", "gateway_example", "api_example"],
                },
            ),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "add_note",
                {"id": "note_example", "element_id": "api_example", "text": 'Public "API"'},
            ),
        )

        assert_mutation_conformance(application, application.snapshot(diagram).to_dict())
        source = application.render(diagram)

        assert '"nodeSeparation": 96.0' in source
        assert 'Public "API"' in source
        assert set(application.diagram_description("architecture-beta").commands) == {
            "configure",
            "add_alignment",
            "add_edge",
            "add_group",
            "add_junction",
            "add_note",
            "add_service",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
            "update_annotation",
            "remove_annotation",
        }

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
        return [line.strip() for line in application.render(diagram).splitlines() if line.strip().startswith("align ")]

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

        with pytest.raises(RuntimeError, match=r"member 'platform' must be a service or junction"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "invalid", "axis": "column", "member_ids": ("client", "platform")},
                ),
            )

    def test_rejects_an_unknown_alignment_axis(self) -> None:
        application, diagram = self._diagram_with_alignment_members()

        with pytest.raises(UnknownCommand, match=r"'add_alignment' has invalid arguments"):
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

        with pytest.raises(RuntimeError, match=r"Relation 'primary' already exists"):
            application.apply(diagram, command)

    def test_rejects_alignment_order_that_contradicts_edge_direction(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_edge",
                {
                    "id": "api_client",
                    "source_id": "client",
                    "target_id": "api",
                    "source_port": "L",
                    "target_port": "R",
                },
            ),
        )

        with pytest.raises(ChangeRejected) as rejected:
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "request_path", "axis": "row", "member_ids": ("client", "api")},
                ),
            )

        violation = rejected.value.report.blocking[0]
        assert violation.code == "constraints.alignments_are_compatible"
        assert violation.path == "relations.request_path"
        assert "edge direction constraint(s) 'api_client' require the reverse order" in violation.message
        assert [relation.id for relation in diagram.find_relations()] == ["api_client"]

    def test_rejects_alignment_on_the_axis_separated_by_an_edge(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "request_row", "axis": "row", "member_ids": ("client", "api")},
            ),
        )

        with pytest.raises(ChangeRejected, match=r"share a row.*'client_api'.*require separation"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_edge",
                    {
                        "id": "client_api",
                        "source_id": "client",
                        "target_id": "api",
                        "source_port": "B",
                        "target_port": "T",
                    },
                ),
            )

        assert [relation.id for relation in diagram.find_relations()] == ["request_row"]

    def test_rejects_overlapping_alignments_on_the_same_axis(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "left", "axis": "row", "member_ids": ("client", "gateway")},
            ),
        )

        with pytest.raises(ChangeRejected) as rejected:
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "right", "axis": "row", "member_ids": ("gateway", "api")},
                ),
            )

        violation = rejected.value.report.blocking[0]
        assert violation.path == "relations.right"
        assert violation.message == "Alignment 'right' overlaps alignment 'left' on row member 'gateway'."

    def test_rejects_two_members_constrained_to_both_a_row_and_a_column(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "request_row", "axis": "row", "member_ids": ("client", "gateway")},
            ),
        )

        with pytest.raises(ChangeRejected, match=r"constrain members 'client', 'gateway' to both a row and a column"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_alignment",
                    {"id": "request_column", "axis": "column", "member_ids": ("client", "gateway")},
                ),
            )

    def test_rejects_edge_direction_conflicting_with_group_column_alignments(self) -> None:
        application, diagram = self._diagram_with_group(2, "client", "api")

        with pytest.raises(ChangeRejected) as rejected:
            application.apply(
                diagram,
                DiagramCommand(
                    "add_edge",
                    {
                        "id": "api_client",
                        "source_id": "client",
                        "target_id": "api",
                        "source_port": "L",
                        "target_port": "R",
                    },
                ),
            )

        violation = rejected.value.report.blocking[0]
        assert violation.path == "elements.platform.columns"
        assert "Alignment 'platform_row_1'" in violation.message
        assert diagram.find_relations() == ()

    def test_rejects_a_restored_snapshot_with_conflicting_layout_constraints(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.apply(
            diagram,
            DiagramCommand(
                "add_edge",
                {"id": "client_api", "source_id": "client", "target_id": "api"},
            ),
        )
        application.apply(
            diagram,
            DiagramCommand(
                "add_alignment",
                {"id": "request_row", "axis": "row", "member_ids": ("client", "api")},
            ),
        )
        payload = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        payload["relations"][0]["fields"]["source_port"]["value"] = "L"
        payload["relations"][0]["fields"]["target_port"]["value"] = "R"

        with pytest.raises(RuntimeError, match=r"Cannot restore invalid diagram 'architecture-beta':.*reverse order"):
            application.restore(payload)

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

        with pytest.raises(UnknownCommand, match=r"'add_group' has invalid arguments"):
            application.apply(
                diagram,
                DiagramCommand("add_group", {"id": "platform", "label": "Platform", "columns": columns}),
            )
