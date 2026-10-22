import json

import pytest

from mermaiden import Application


class TestClassDiagram:
    def test_restores_a_populated_diagram_with_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        for command in (
            ("configure", {"wrap": False}),
            ("add_namespace", {"id": "domain_example", "label": "Domain", "comment": "Types"}),
            (
                "add_class",
                {
                    "id": "animal_example",
                    "label": 'Animal "kind"',
                    "parent_id": "domain_example",
                    "attributes": [{"name": "name", "type": {"name": "String"}, "visibility": "public"}],
                    "methods": [{"name": "sound", "return_type": {"name": "void"}, "visibility": "public"}],
                    "annotations": ["abstract"],
                },
            ),
            ("add_class", {"id": "duck_example", "label": "Duck", "parent_id": "domain_example"}),
            (
                "add_relation",
                {
                    "id": "inherits_example",
                    "source_id": "duck_example",
                    "target_id": "animal_example",
                    "relation_kind": "inheritance",
                    "label": "extends",
                },
            ),
            ("add_note", {"id": "note_example", "class_id": "animal_example", "text": 'Base "type"'}),
        ):
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert 'namespace c_v_domain_example["Domain"]' in source
        assert "abstract" in source
        assert "--|>" in source
        assert "note for c_v_animal_example" in source
        assert application.render(restored) == source

    @pytest.mark.parametrize(
        ("relation_kind", "connector"),
        (
            ("association", "--"),
            ("inheritance", "--|>"),
            ("composition", "--*"),
            ("aggregation", "--o"),
            ("dependency", "..>"),
            ("realization", "..|>"),
        ),
    )
    def test_relation_markers_follow_semantic_source_to_target_through_update_and_restore(
        self, relation_kind: str, connector: str
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "source_example", "label": "Source"})
        application.execute(diagram, "add_class", {"id": "target_example", "label": "Target"})
        application.execute(diagram, "add_class", {"id": "new_target_example", "label": "New target_example"})
        application.execute(
            diagram,
            "add_relation",
            {
                "id": "relation_example",
                "source_id": "source_example",
                "target_id": "target_example",
                "relation_kind": relation_kind,
                "label": "uses",
                "source_label": "one_example",
                "target_label": "many",
            },
        )
        source = application.render(diagram)
        assert f'c_v_source_example "one_example" {connector} "many" c_v_target_example : uses' in source
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert application.render(restored) == source
        application.execute(
            restored,
            "update_relation",
            {
                "id": "relation_example",
                "kind": "class_relation",
                "changes": {"element_ids": ["source_example", "new_target_example"]},
            },
        )
        updated_source = application.render(restored)
        assert f'c_v_source_example "one_example" {connector} "many" c_v_new_target_example : uses' in updated_source
        updated = application.restore(json.loads(json.dumps(application.snapshot(restored).to_dict())))
        assert application.render(updated) == updated_source

    def test_rejects_bad_relations_duplicate_classes_and_unknown_note_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "one_example", "label": "One"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_relation", {"id": "bad_example"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_relation",
                {
                    "id": "syntax_example",
                    "source_id": "one_example",
                    "target_id": "one_example",
                    "relation_kind": "<|--",
                },
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_class", {"id": "one_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_note", {"id": "note_example", "class_id": "missing_example", "text": "No"}
            )

    def test_empty_namespace_persists_as_a_draft_and_becomes_renderable_when_populated(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_namespace", {"id": "sales_example", "label": "Sales"})
        payload = application.snapshot(diagram).to_dict()
        restored = application.restore(json.loads(json.dumps(payload)))
        assert payload["draft"] is True
        assert application.snapshot(restored).to_dict() == payload
        report = application.validate_render(restored)
        assert not report.success
        assert not report.svg
        assert report.diagnostics[0].code == "diagram_invalid"
        with pytest.raises(RuntimeError, match=r"requires a class"):
            application.render(restored)
        application.execute(
            restored, "add_class", {"id": "order_example", "label": "Order", "parent_id": "sales_example"}
        )
        assert application.snapshot(restored).draft is False
        assert 'namespace c_v_sales_example["Sales"]' in application.render(restored)

    @pytest.mark.parametrize(
        "operation,arguments",
        (
            ("remove_element", {"id": "order_example"}),
            ("move_element", {"id": "order_example", "kind": "class", "parent_id": ""}),
        ),
    )
    def test_removing_the_last_namespace_child_is_rejected_without_losing_the_child(
        self, operation: str, arguments: dict[str, object]
    ) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_namespace", {"id": "sales_example", "label": "Sales"})
        application.execute(
            diagram, "add_class", {"id": "order_example", "label": "Order", "parent_id": "sales_example"}
        )
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        with pytest.raises(RuntimeError, match=r"requires a class"):
            application.execute(diagram, operation, arguments)
        assert application.snapshot(diagram).to_dict() == before
        assert application.render(diagram) == source
        application.execute(
            diagram, "add_class", {"id": "invoice_example", "label": "Invoice", "parent_id": "sales_example"}
        )
        application.execute(diagram, operation, arguments)
        assert application.snapshot(diagram).draft is False
        assert 'c_v_invoice_example["Invoice"]' in application.render(diagram)

    @pytest.mark.parametrize("operation", ("add_note", "update_annotation"))
    def test_a_note_cannot_target_a_namespace(self, operation: str) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_namespace", {"id": "sales_example", "label": "Sales"})
        application.execute(
            diagram, "add_class", {"id": "order_example", "label": "Order", "parent_id": "sales_example"}
        )
        application.execute(
            diagram, "add_note", {"id": "note_example", "class_id": "order_example", "text": "Pay before shipping"}
        )
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        with pytest.raises(RuntimeError, match=r"class"):
            if operation == "add_note":
                application.execute(
                    diagram, operation, {"id": "new_example", "class_id": "sales_example", "text": "Sales note_example"}
                )
            else:
                application.execute(
                    diagram,
                    operation,
                    {
                        "id": "note_example",
                        "kind": "class_note",
                        "changes": {"targets": [{"kind": "element", "id": "sales_example"}]},
                    },
                )
        assert application.snapshot(diagram).to_dict() == before
        assert application.render(diagram) == source

    @pytest.mark.parametrize(
        "targets",
        (
            [],
            [{"kind": "element", "id": "order_example"}, {"kind": "element", "id": "invoice_example"}],
            [{"kind": "relation", "id": "billing_example"}],
        ),
    )
    def test_note_target_edits_reject_unsupported_cardinality_and_kinds(self, targets: list[dict[str, str]]) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "order_example", "label": "Order"})
        application.execute(diagram, "add_class", {"id": "invoice_example", "label": "Invoice"})
        application.execute(
            diagram,
            "add_relation",
            {"id": "billing_example", "source_id": "order_example", "target_id": "invoice_example"},
        )
        application.execute(
            diagram, "add_note", {"id": "note_example", "class_id": "order_example", "text": "Pay before shipping"}
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "update_annotation",
                {"id": "note_example", "kind": "class_note", "changes": {"targets": targets}},
            )
        assert application.snapshot(diagram).to_dict() == before
        application.execute(
            diagram,
            "update_annotation",
            {
                "id": "note_example",
                "kind": "class_note",
                "changes": {"targets": [{"kind": "element", "id": "invoice_example"}]},
            },
        )
        assert 'note for c_v_invoice_example "Pay before shipping"' in application.render(diagram)
        assert "note for c_v_order_example" not in application.render(diagram)

    @pytest.mark.parametrize("text", ("", " ", "Pay\nnow", "Pay\x00now"))
    @pytest.mark.parametrize("operation", ("add_note", "update_annotation"))
    def test_invalid_note_text_is_rejected_without_changing_existing_notes(self, text: str, operation: str) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.execute(diagram, "add_class", {"id": "order_example", "label": "Order"})
        application.execute(
            diagram, "add_note", {"id": "note_example", "class_id": "order_example", "text": "Pay before shipping"}
        )
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"text"):
            if operation == "add_note":
                application.execute(
                    diagram, operation, {"id": "new_example", "class_id": "order_example", "text": text}
                )
            else:
                application.execute(
                    diagram, operation, {"id": "note_example", "kind": "class_note", "changes": {"text": text}}
                )
        assert application.snapshot(diagram).to_dict() == before
