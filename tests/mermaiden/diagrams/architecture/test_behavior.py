import json
from typing import Any

import pytest

from mermaiden import Application


class TestArchitecture:
    def test_exercises_note_and_configuration_commands(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.execute(diagram, "configure", {"nodeSeparation": 96, "seed": 7})
        application.execute(diagram, "add_group", {"id": "group_example", "label": "Group Example"})
        application.execute(diagram, "add_service", {"id": "client_example", "label": "Client Example"})
        application.execute(diagram, "add_junction", {"id": "gateway_example", "label": "Gateway Example"})
        application.execute(diagram, "add_service", {"id": "api_example", "label": "API Example"})
        application.execute(
            diagram,
            "add_edge",
            {"id": "edge_example", "source_id": "client_example", "target_id": "api_example", "label": "HTTPS Example"},
        )
        application.execute(
            diagram,
            "add_alignment",
            {
                "id": "alignment_example",
                "axis": "row",
                "member_ids": ["client_example", "gateway_example", "api_example"],
            },
        )
        application.execute(
            diagram, "add_note", {"id": "note_example", "element_id": "api_example", "text": 'Public "API"'}
        )
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
        application.execute(diagram, "add_service", {"id": "client_example", "label": "Client"})
        application.execute(diagram, "add_junction", {"id": "gateway_example", "label": "Gateway"})
        application.execute(diagram, "add_service", {"id": "api_example", "label": "API"})
        return (application, diagram)

    def _diagram_with_group(self, columns: int, *member_ids: str) -> tuple[Application, Any]:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.execute(diagram, "add_group", {"id": "platform_example", "label": "Platform", "columns": columns})
        for member_id in member_ids:
            application.execute(
                diagram, "add_service", {"id": member_id, "label": member_id.upper(), "group_id": "platform_example"}
            )
        return (application, diagram)

    def _alignment_directives(self, application: Application, diagram: Any) -> list[str]:
        return [line.strip() for line in application.render(diagram).splitlines() if line.strip().startswith("align ")]

    def test_renders_and_restores_a_quoted_edge_label(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.execute(diagram, "add_service", {"id": "client_example", "label": "Client"})
        application.execute(diagram, "add_service", {"id": "api_example", "label": "API"})
        application.execute(
            diagram,
            "add_edge",
            {
                "id": "client_api_example",
                "source_id": "client_example",
                "target_id": "api_example",
                "label": 'HTTPS "mTLS"',
            },
        )
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert 'client_example:R -["HTTPS \\"mTLS\\""]-> L:api_example' in source
        assert application.render(restored) == source

    def test_keeps_an_empty_edge_label_compact(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        application.execute(diagram, "add_service", {"id": "client_example", "label": "Client"})
        application.execute(diagram, "add_service", {"id": "api_example", "label": "API"})
        application.execute(
            diagram, "add_edge", {"id": "client_api_example", "source_id": "client_example", "target_id": "api_example"}
        )
        assert "client_example:R --> L:api_example" in application.render(diagram)

    @pytest.mark.parametrize(
        ("axis", "directive"),
        (
            ("row", "align row client_example gateway_example api_example"),
            ("column", "align column client_example gateway_example api_example"),
        ),
    )
    def test_renders_and_restores_an_ordered_alignment(self, axis: str, directive: str) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram,
            "add_alignment",
            {"id": "primary_example", "axis": axis, "member_ids": ["client_example", "gateway_example", "api_example"]},
        )
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert directive in source
        assert source.index("service api_example") < source.index(directive)
        assert application.render(restored) == source

    @pytest.mark.parametrize(
        ("member_ids", "message"),
        (
            (("client_example",), "requires at least two members"),
            (("client_example", "client_example"), "members must be unique"),
            (("client_example", "missing"), "references unknown member 'missing'"),
        ),
    )
    def test_rejects_invalid_alignment_members(self, member_ids: tuple[str, ...], message: str) -> None:
        application, diagram = self._diagram_with_alignment_members()
        with pytest.raises(RuntimeError, match=message):
            application.execute(
                diagram, "add_alignment", {"id": "invalid_example", "axis": "row", "member_ids": member_ids}
            )

    def test_rejects_groups_as_alignment_members(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(diagram, "add_group", {"id": "platform_example", "label": "Platform"})
        with pytest.raises(RuntimeError, match=r"member 'platform_example' must be a service or junction"):
            application.execute(
                diagram,
                "add_alignment",
                {"id": "invalid_example", "axis": "column", "member_ids": ("client_example", "platform_example")},
            )

    def test_rejects_an_unknown_alignment_axis(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        with pytest.raises(RuntimeError, match=r"'add_alignment' has invalid arguments"):
            application.execute(
                diagram,
                "add_alignment",
                {"id": "invalid_example", "axis": "diagonal", "member_ids": ("client_example", "gateway_example")},
            )

    def test_rejects_mermaid_port_tokens(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        with pytest.raises(RuntimeError, match=r"'add_edge' has invalid arguments"):
            application.execute(
                diagram,
                "add_edge",
                {
                    "id": "syntax_example",
                    "source_id": "client_example",
                    "target_id": "api_example",
                    "source_port": "R",
                    "target_port": "L",
                },
            )

    def test_rejects_duplicate_alignment_ids(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        command = (
            "add_alignment",
            {"id": "primary_example", "axis": "row", "member_ids": ("client_example", "gateway_example")},
        )
        application.execute(diagram, *command)
        with pytest.raises(RuntimeError, match=r"Relation 'primary_example' already exists"):
            application.execute(diagram, *command)

    def test_rejects_alignment_order_that_contradicts_edge_direction(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram,
            "add_edge",
            {
                "id": "api_client_example",
                "source_id": "client_example",
                "target_id": "api_example",
                "source_port": "left",
                "target_port": "right",
            },
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(
            RuntimeError, match=r"edge direction constraint\(s\) 'api_client_example' require the reverse order"
        ):
            application.execute(
                diagram,
                "add_alignment",
                {"id": "request_path_example", "axis": "row", "member_ids": ("client_example", "api_example")},
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_alignment_on_the_axis_separated_by_an_edge(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram,
            "add_alignment",
            {"id": "request_row_example", "axis": "row", "member_ids": ("client_example", "api_example")},
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"share a row.*'client_api_example'.*require separation"):
            application.execute(
                diagram,
                "add_edge",
                {
                    "id": "client_api_example",
                    "source_id": "client_example",
                    "target_id": "api_example",
                    "source_port": "bottom",
                    "target_port": "top",
                },
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_overlapping_alignments_on_the_same_axis(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram,
            "add_alignment",
            {"id": "left_example", "axis": "row", "member_ids": ("client_example", "gateway_example")},
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(
            RuntimeError,
            match=r"Alignment 'right_example' overlaps alignment 'left_example' on row member 'gateway_example'",
        ):
            application.execute(
                diagram,
                "add_alignment",
                {"id": "right_example", "axis": "row", "member_ids": ("gateway_example", "api_example")},
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_two_members_constrained_to_both_a_row_and_a_column(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram,
            "add_alignment",
            {"id": "request_row_example", "axis": "row", "member_ids": ("client_example", "gateway_example")},
        )
        with pytest.raises(
            RuntimeError, match=r"constrain members 'client_example', 'gateway_example' to both a row and a column"
        ):
            application.execute(
                diagram,
                "add_alignment",
                {"id": "request_column_example", "axis": "column", "member_ids": ("client_example", "gateway_example")},
            )

    def test_rejects_edge_direction_conflicting_with_group_column_alignments(self) -> None:
        application, diagram = self._diagram_with_group(2, "client_example", "api_example")
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"Alignment 'platform_example_row_1'"):
            application.execute(
                diagram,
                "add_edge",
                {
                    "id": "api_client_example",
                    "source_id": "client_example",
                    "target_id": "api_example",
                    "source_port": "left",
                    "target_port": "right",
                },
            )
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_a_restored_snapshot_with_conflicting_layout_constraints(self) -> None:
        application, diagram = self._diagram_with_alignment_members()
        application.execute(
            diagram, "add_edge", {"id": "client_api_example", "source_id": "client_example", "target_id": "api_example"}
        )
        application.execute(
            diagram,
            "add_alignment",
            {"id": "request_row_example", "axis": "row", "member_ids": ("client_example", "api_example")},
        )
        payload = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        payload["relations"][0]["fields"]["source_port"]["value"] = "left"
        payload["relations"][0]["fields"]["target_port"]["value"] = "right"
        with pytest.raises(RuntimeError, match=r"Cannot restore invalid diagram 'architecture-beta':.*reverse order"):
            application.restore(payload)

    def test_derives_a_grid_from_direct_members_without_persisting_alignments(self) -> None:
        application, diagram = self._diagram_with_group(2, "a")
        application.execute(
            diagram,
            "add_group",
            {"id": "nested_example", "label": "Nested", "parent_id": "platform_example", "columns": 1},
        )
        for member_id in ("x", "y"):
            application.execute(
                diagram, "add_service", {"id": member_id, "label": member_id.upper(), "group_id": "nested_example"}
            )
        for member_id in ("b", "c", "d"):
            application.execute(
                diagram, "add_junction", {"id": member_id, "label": member_id.upper(), "group_id": "platform_example"}
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
        assert "align row a nested_example" not in source
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
        self, columns: int, member_ids: tuple[str, ...], directives: list[str]
    ) -> None:
        application, diagram = self._diagram_with_group(columns, *member_ids)
        assert self._alignment_directives(application, diagram) == directives

    @pytest.mark.parametrize("columns", (0, -1))
    def test_rejects_non_positive_group_columns(self, columns: int) -> None:
        application = Application.create()
        diagram = application.create_diagram("architecture-beta")
        with pytest.raises(RuntimeError, match=r"'add_group' has invalid arguments"):
            application.execute(
                diagram, "add_group", {"id": "platform_example", "label": "Platform", "columns": columns}
            )
