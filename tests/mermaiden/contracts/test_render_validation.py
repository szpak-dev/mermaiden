import json
from xml.etree import ElementTree

import pytest

from mermaiden import Application


class TestSequenceAndStateTextRendering:
    def test_sequence_text_survives_updates_source_projection_and_snapshot_restore(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(diagram, "add_box", {"id": "box_example", "label": "Old Box Example"})
        application.execute(
            diagram,
            "add_participant",
            {
                "id": "first_example",
                "label": "Old First Example",
                "kind": "actor",
                "box_id": "box_example",
            },
        )
        application.execute(
            diagram,
            "add_participant",
            {"id": "second_example", "label": "Second Example", "kind": "control"},
        )
        application.execute(diagram, "control", {"id": "control_example", "kind": "loop", "label": "Old Loop"})
        application.execute(
            diagram,
            "add_message",
            {
                "id": "message_example",
                "source_id": "first_example",
                "target_id": "second_example",
                "label": "Old Message Example",
            },
        )
        application.execute(diagram, "control", {"id": "end_example", "kind": "end"})
        application.execute(
            diagram,
            "add_note",
            {
                "id": "note_example",
                "participant_ids": ["first_example", "second_example"],
                "position": "over",
                "text": "Old Note Example",
            },
        )

        application.execute(
            diagram,
            "update_element",
            {
                "id": "box_example",
                "kind": "participant_box",
                "changes": {"label": "Box; literal #59; example"},
            },
        )
        application.execute(
            diagram,
            "update_element",
            {
                "id": "first_example",
                "kind": "participant",
                "changes": {"label": "Participant; literal #59; example"},
            },
        )
        application.execute(
            diagram,
            "update_relation",
            {
                "id": "message_example",
                "kind": "message",
                "changes": {"label": "Message; literal #59; example"},
            },
        )
        application.execute(
            diagram,
            "update_relation",
            {
                "id": "control_example",
                "kind": "control",
                "changes": {"label": "Loop; literal #59; example"},
            },
        )
        application.execute(
            diagram,
            "update_annotation",
            {
                "id": "note_example",
                "kind": "sequence_note",
                "changes": {"text": "Note; literal #59; example"},
            },
        )

        snapshot = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(snapshot)))

        for original, encoded in (
            ("Box; literal #59; example", "box Box#59; literal #35;59#59; example"),
            (
                "Participant; literal #59; example",
                "actor first_example as Participant#59; literal #35;59#59; example",
            ),
            ("Message; literal #59; example", ": Message#59; literal #35;59#59; example"),
            ("Loop; literal #59; example", "loop Loop#59; literal #35;59#59; example"),
            ("Note; literal #59; example", ": Note#59; literal #35;59#59; example"),
        ):
            assert original in json.dumps(snapshot)
            assert encoded in source
        assert application.snapshot(restored).to_dict() == snapshot
        assert application.render(restored) == source

    @pytest.mark.integration
    def test_sequence_text_with_semicolons_and_literal_entities_is_visible_in_svg(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        expected = (
            "Box; literal #59; example",
            "Participant; literal #59; example",
            "Message; literal #59; example",
            "Loop; literal #59; example",
            "Note; literal #59; example",
        )
        application.execute(diagram, "add_box", {"id": "box_example", "label": expected[0]})
        application.execute(
            diagram,
            "add_participant",
            {"id": "first_example", "label": expected[1], "kind": "actor", "box_id": "box_example"},
        )
        application.execute(
            diagram,
            "add_participant",
            {"id": "second_example", "label": "Second Example", "kind": "control"},
        )
        application.execute(diagram, "control", {"id": "control_example", "kind": "loop", "label": expected[3]})
        application.execute(
            diagram,
            "add_message",
            {
                "id": "message_example",
                "source_id": "first_example",
                "target_id": "second_example",
                "label": expected[2],
            },
        )
        application.execute(diagram, "control", {"id": "end_example", "kind": "end"})
        application.execute(
            diagram,
            "add_note",
            {
                "id": "note_example",
                "participant_ids": ["first_example", "second_example"],
                "position": "over",
                "text": expected[4],
            },
        )
        before = application.snapshot(diagram).to_dict()

        report = application.validate_render(diagram)

        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        text = " ".join(
            "".join(element.itertext())
            for element in svg.iter()
            if element.tag in {"{http://www.w3.org/2000/svg}text", "{http://www.w3.org/1999/xhtml}span"}
        )
        for value in expected:
            assert value in text
        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.integration
    def test_state_note_with_semicolons_remains_visible_without_snapshot_mutation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("stateDiagram-v2")
        application.execute(diagram, "add_state", {"id": "state_example", "label": "State Example"})
        application.execute(
            diagram,
            "add_note",
            {
                "id": "note_example",
                "state_id": "state_example",
                "position": "left",
                "text": "Annotation; proof",
            },
        )
        before = application.snapshot(diagram).to_dict()

        source = application.render(diagram)
        report = application.validate_render(diagram)

        assert '"Annotation; proof"' in source
        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        text = " ".join(
            "".join(element.itertext())
            for element in svg.iter()
            if element.tag in {"{http://www.w3.org/2000/svg}text", "{http://www.w3.org/1999/xhtml}span"}
        )
        assert "Annotation" in text
        assert ";" in text
        assert "proof" in text
        assert application.snapshot(diagram).to_dict() == before


class TestRenderValidation:
    @pytest.mark.integration
    def test_class_relation_markers_render_at_every_semantic_target(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        markers = {
            "inheritance": "extensionEnd",
            "composition": "compositionEnd",
            "aggregation": "aggregationEnd",
            "dependency": "dependencyEnd",
            "realization": "extensionEnd",
        }
        for relation_kind in markers:
            application.execute(
                diagram,
                "add_class",
                {"id": f"{relation_kind}_source", "label": f"{relation_kind} source"},
            )
            application.execute(
                diagram,
                "add_class",
                {"id": f"{relation_kind}_target", "label": f"{relation_kind} target"},
            )
            application.execute(
                diagram,
                "add_relation",
                {
                    "id": relation_kind,
                    "source_id": f"{relation_kind}_source",
                    "target_id": f"{relation_kind}_target",
                    "relation_kind": relation_kind,
                },
            )

        report = application.validate_render(diagram)

        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        relation_paths = tuple(
            element for element in svg.iter() if "relation" in element.attrib.get("class", "").split()
        )
        assert len(relation_paths) == len(markers)
        for relation_kind, marker in markers.items():
            path = next(
                element
                for element in relation_paths
                if f"c_v_{relation_kind}_source_c_v_{relation_kind}_target" in element.attrib["id"]
            )
            assert "marker-start" not in path.attrib
            assert path.attrib["marker-end"].endswith(f"classDiagram-{marker}-margin)")

    @pytest.mark.integration
    def test_renderer_rejects_a_real_exit_zero_mermaid_error_svg(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        for index in range(550):
            application.execute(
                diagram,
                "add_class",
                {
                    "id": f"class_{index}_{'x' * 180}",
                    "label": f"Oversized {index}",
                    "comment": f"Contract evidence {index} {'y' * 80}",
                    "attributes": [{"name": f"field_{field}", "type": {"name": "string"}} for field in range(20)],
                    "annotations": ["injectable", "immutable"],
                },
            )

        report = application.validate_render(diagram)

        assert not report.success
        assert report.diagnostics[0].code == "svg_error"
        assert report.diagnostics[0].message == "Mermaid produced an error SVG."
        assert "Maximum text size in diagram exceeded" in report.diagnostics[0].details

    @pytest.mark.integration
    def test_class_text_preserves_slashes_in_mermaid_source_and_svg(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "diagrams/api", "label": "diagrams/api"})

        snapshot = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        report = application.validate_render(diagram)
        assert '"id": "diagrams/api"' in json.dumps(snapshot)
        assert '["diagrams/api"]' in source
        assert "#47;" not in source
        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        assert any("diagrams/api" in "".join(element.itertext()) for element in svg.iter())
        assert "&#47;" not in report.svg

    @pytest.mark.integration
    def test_er_source_path_identities_render_without_changing_snapshot_identity(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("erDiagram")
        project_id = "src/enclosure/projects/models.py::class:enclosure.projects.models.Project"
        publication_id = (
            "src/enclosure/projects/models.py::class:enclosure.projects.models.ArchitectureContractPublication"
        )
        application.execute(diagram, "add_entity", {"id": project_id, "label": "PROJECT"})
        application.execute(diagram, "add_entity", {"id": publication_id, "label": "PUBLICATION"})
        application.execute(
            diagram,
            "add_relationship",
            {
                "id": "project_publications",
                "source_id": project_id,
                "target_id": publication_id,
                "label": "publishes",
                "target_cardinality": "zero_or_more",
            },
        )

        snapshot = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        report = application.validate_render(application.restore(snapshot))

        assert project_id in json.dumps(snapshot)
        assert project_id not in source
        assert "e_h_" in source
        assert report.success, report.diagnostics

    @pytest.mark.integration
    def test_class_text_is_rendered_literally_in_labels_relations_and_notes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_namespace", {"id": "sales", "label": "Old name"})
        application.execute(diagram, "add_class", {"id": "Order[Item]", "label": 'Order "żółć"', "parent_id": "sales"})
        application.execute(diagram, "add_class", {"id": "invoice", "label": "Invoice"})
        application.execute(
            diagram,
            "update_element",
            {
                "id": "sales",
                "kind": "class_namespace",
                "changes": {"label": 'Sales "core"'},
            },
        )
        application.execute(
            diagram,
            "add_relation",
            {
                "id": "billing",
                "source_id": "Order[Item]",
                "target_id": "invoice",
                "label": "bills: order",
                "source_label": 'one "order"',
                "target_label": "0..*",
            },
        )
        application.execute(
            diagram,
            "add_note",
            {
                "id": "note",
                "class_id": "Order[Item]",
                "text": 'Use "quotes"; <b>literal</b> & #quot;',
            },
        )
        before = application.snapshot(diagram).to_dict()

        report = application.validate_render(application.restore(before))

        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        text = " ".join(
            "".join(element.itertext())
            for element in svg.iter()
            if element.tag in {"{http://www.w3.org/2000/svg}text", "{http://www.w3.org/1999/xhtml}span"}
        )
        for label in (
            'Order "żółć"',
            'Sales "core"',
            "Invoice",
            "bills: order",
            'one "order"',
            "0..*",
            'Use "quotes"; <b>literal</b> & #quot;',
        ):
            assert label in text
        assert "Old name" not in text
        assert "#59;" not in application.render(diagram)
        assert application.snapshot(diagram).to_dict() == before

    @pytest.mark.integration
    def test_class_members_render_with_their_types_visibility_and_parameter_order(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(
            diagram,
            "add_class",
            {
                "id": "catalog",
                "label": "Catalog",
                "attributes": [
                    {
                        "name": "items",
                        "type": {"name": "Map", "arguments": [{"name": "Key"}, {"name": "Value"}]},
                        "visibility": "private",
                    },
                    {"name": "count", "type": {"name": "int"}, "visibility": "protected", "static": True},
                ],
                "methods": [
                    {
                        "name": "find",
                        "return_type": {
                            "name": "Map",
                            "arguments": [
                                {"name": "Key"},
                                {
                                    "name": "List",
                                    "arguments": [
                                        {
                                            "name": "Pair",
                                            "arguments": [{"name": "Left"}, {"name": "Right"}],
                                        }
                                    ],
                                },
                            ],
                        },
                        "visibility": "public",
                        "parameters": [
                            {
                                "name": "key",
                                "type": {
                                    "name": "Map",
                                    "arguments": [
                                        {"name": "Key"},
                                        {"name": "List", "arguments": [{"name": "Value"}]},
                                    ],
                                },
                            },
                            {"name": "limit", "type": {"name": "int"}},
                        ],
                    },
                    {
                        "name": "refresh",
                        "return_type": {"name": "void"},
                        "visibility": "package",
                        "modifier": "abstract",
                    },
                ],
            },
        )

        report = application.validate_render(diagram)

        assert report.success, report.diagnostics
        svg = ElementTree.fromstring(report.svg)
        text = " ".join(
            "".join(element.itertext())
            for element in svg.iter()
            if element.tag in {"{http://www.w3.org/2000/svg}text", "{http://www.w3.org/1999/xhtml}span"}
        )
        for member in (
            "-Map<Key, Value> items",
            "#int count",
            "+find(Map<Key, List<Value>> key, int limit)",
            "Map<Key, List<Pair<Left, Right>>>",
            "~refresh()",
            "void",
        ):
            assert member in text
        assert any(
            "".join(element.itertext()) == "#int count" and "underline" in element.attrib.get("style", "")
            for element in svg.iter()
        )
        assert any(
            "".join(element.itertext()).startswith("~refresh()") and "italic" in element.attrib.get("style", "")
            for element in svg.iter()
        )

    def test_draft_diagram_can_be_persisted_but_not_rendered(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")

        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(payload)
        report = application.validate_render(diagram)

        assert application.snapshot(restored).to_dict() == payload
        assert not report.success
        assert report.diagram_id == "sequenceDiagram"
        assert report.mermaid_version == application.mermaid_version
        assert report.mermaid_cli_version == application.mermaid_cli_version
        assert report.diagnostics[0].code == "diagram_invalid"
        assert "Diagram requires at least one element" in report.diagnostics[0].details
        with pytest.raises(RuntimeError, match="Cannot render invalid diagram 'sequenceDiagram'"):
            application.render(restored)

    def test_a_valid_snapshot_tampered_into_an_invalid_state_cannot_be_restored(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(
            diagram,
            "add_participant",
            {"id": "participant_example", "label": "Participant Example"},
        )
        payload = application.snapshot(diagram).to_dict()
        payload["elements"] = []

        with pytest.raises(RuntimeError, match="Cannot restore invalid diagram 'sequenceDiagram'"):
            application.restore(payload)

    @pytest.mark.integration
    def test_full_render_validation_is_a_non_mutating_application_operation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(
            diagram,
            "add_participant",
            {"id": "participant_example", "label": "Participant Example"},
        )
        before = application.snapshot(diagram).to_dict()

        report = application.validate_render(diagram)

        assert report.success
        assert report.diagram_id == "sequenceDiagram"
        assert report.mermaid_version == application.mermaid_version
        assert report.mermaid_cli_version == application.mermaid_cli_version
        assert report.svg.startswith("<svg")
        assert not report.diagnostics
        assert application.snapshot(diagram).to_dict() == before
