import json
from typing import cast

import pytest

from mermaiden import Application


class TestTreeView:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        commands = (
            ("configure", {"wrap": False}),
            ("add_directory", {"id": "root_example", "label": "root_example"}),
            ("add_item", {"id": "child_example", "label": 'child_example "one"'}),
            ("classify_item", {"id": "child_example", "item_type": "file"}),
            ("add_file", {"id": "readme_example", "label": "README.md"}),
            ("add_branch", {"id": "branch_example", "parent_id": "root_example", "child_id": "child_example"}),
            ("add_branch", {"id": "readme_branch_example", "parent_id": "root_example", "child_id": "readme_example"}),
            (
                "add_annotation",
                {
                    "id": "annotation_example",
                    "element_id": "child_example",
                    "highlight": True,
                    "icon": "folder",
                    "description": "Docs",
                },
            ),
        )
        for operation, arguments in commands:
            application.execute(diagram, operation, arguments)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("treeView-beta").commands) == {
            operation for operation, _arguments in commands
        } | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
            "update_annotation",
            "remove_annotation",
        }
        assert "root_example/" in source
        assert '"child_example \\"one\\"" :::highlight icon(folder) ## Docs' in source
        assert "  README.md" in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_and_unknown_annotation_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        application.execute(diagram, "add_directory", {"id": "root_example", "label": "root_example"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"missing_example": True})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_item", {"id": "root_example", "label": "again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_annotation",
                {"id": "annotation_example", "element_id": "missing_example", "description": "Missing"},
            )

    def test_rejects_unsupported_icon_characters_before_create_or_update(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        application.execute(diagram, "add_directory", {"id": "root_example", "label": "Root"})
        before_create = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError) as rejected_create:
            application.execute(
                diagram, "add_annotation", {"id": "note_example", "element_id": "root_example", "icon": "📁"}
            )
        diagnostic = str(rejected_create.value)
        assert "add_annotation" in diagnostic
        assert "icon" in diagnostic
        assert "'📁' (U+1F4C1)" in diagnostic
        assert "rule pattern" in diagnostic
        assert application.snapshot(diagram).to_dict() == before_create
        application.execute(
            diagram, "add_annotation", {"id": "note_example", "element_id": "root_example", "icon": "folder"}
        )
        before_update = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError) as rejected_update:
            application.execute(
                diagram,
                "update_annotation",
                {"id": "note_example", "kind": "tree_annotation", "changes": {"icon": "📁"}},
            )
        diagnostic = str(rejected_update.value)
        assert "update_annotation" in diagnostic
        assert "changes.icon" in diagnostic
        assert "'📁' (U+1F4C1)" in diagnostic
        assert application.snapshot(diagram).to_dict() == before_update

    def test_rejects_unsupported_icon_characters_during_restore(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        application.execute(diagram, "add_directory", {"id": "root_example", "label": "Root"})
        application.execute(
            diagram, "add_annotation", {"id": "note_example", "element_id": "root_example", "icon": "folder"}
        )
        payload = application.snapshot(diagram).to_dict()
        annotations = cast(list[dict[str, object]], payload["annotations"])
        fields = cast(dict[str, object], annotations[0]["fields"])
        fields["icon"] = "📁"
        with pytest.raises(ValueError, match=r"icon"):
            application.restore(payload)

    @pytest.mark.parametrize("operation", ["add_directory", "add_file"])
    @pytest.mark.parametrize("label", ["src/package", "src\\package"])
    def test_rejects_typed_paths_atomically(self, operation: str, label: str) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        before = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"basename without path separators"):
            application.execute(diagram, operation, {"id": "nested_example", "label": label})
        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_file_parents_and_invalid_reclassification_atomically(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        application.execute(diagram, "add_directory", {"id": "root_example", "label": "root_example"})
        application.execute(diagram, "add_file", {"id": "leaf_example", "label": "leaf_example.txt"})
        application.execute(diagram, "add_item", {"id": "child_example", "label": "child_example"})
        before_branch = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"File 'leaf_example' cannot be the parent"):
            application.execute(
                diagram,
                "add_branch",
                {"id": "invalid_example", "parent_id": "leaf_example", "child_id": "child_example"},
            )
        assert application.snapshot(diagram).to_dict() == before_branch
        application.execute(
            diagram, "add_branch", {"id": "valid_example", "parent_id": "root_example", "child_id": "leaf_example"}
        )
        before_classification = application.snapshot(diagram).to_dict()
        with pytest.raises(RuntimeError, match=r"File 'root_example' cannot be the parent"):
            application.execute(diagram, "classify_item", {"id": "root_example", "item_type": "file"})
        assert application.snapshot(diagram).to_dict() == before_classification

    def test_removes_the_complete_branch_subtree_and_its_dependants_atomically(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        for operation, arguments in (
            ("add_directory", {"id": "root_example", "label": "root_example"}),
            ("add_directory", {"id": "nested_example", "label": "nested_example"}),
            ("add_file", {"id": "leaf_example", "label": "leaf_example.txt"}),
            ("add_file", {"id": "sibling_example", "label": "sibling_example.txt"}),
            ("add_directory", {"id": "outside_example", "label": "outside_example"}),
            ("add_branch", {"id": "root_nested_example", "parent_id": "root_example", "child_id": "nested_example"}),
            ("add_branch", {"id": "nested_leaf_example", "parent_id": "nested_example", "child_id": "leaf_example"}),
            ("add_branch", {"id": "root_sibling_example", "parent_id": "root_example", "child_id": "sibling_example"}),
            ("add_annotation", {"id": "root_note_example", "element_id": "root_example", "highlight": True}),
            ("add_annotation", {"id": "nested_note_example", "element_id": "nested_example", "highlight": True}),
            ("add_annotation", {"id": "leaf_note_example", "element_id": "leaf_example", "highlight": True}),
            ("add_annotation", {"id": "sibling_note_example", "element_id": "sibling_example", "highlight": True}),
            ("add_annotation", {"id": "outside_note_example", "element_id": "outside_example", "highlight": True}),
        ):
            application.execute(diagram, operation, arguments)
        before = application.snapshot(diagram).to_dict()
        source = application.render(diagram)
        with pytest.raises(RuntimeError, match=r"still has dependants; use cascade=True"):
            application.execute(diagram, "remove_element", {"id": "root_example"})
        assert application.snapshot(diagram).to_dict() == before
        assert application.render(diagram) == source
        report = application.execute(diagram, "remove_element", {"id": "root_example", "cascade": True})
        assert report is not None
        assert tuple((item.kind, item.id) for item in report.removed) == (
            ("element", "root_example"),
            ("element", "nested_example"),
            ("element", "leaf_example"),
            ("element", "sibling_example"),
            ("relation", "root_nested_example"),
            ("relation", "nested_leaf_example"),
            ("relation", "root_sibling_example"),
            ("annotation", "root_note_example"),
            ("annotation", "nested_note_example"),
            ("annotation", "leaf_note_example"),
            ("annotation", "sibling_note_example"),
        )
        assert application.snapshot(diagram).to_dict()["relations"] == []
        assert application.render(diagram).endswith("treeView-beta\noutside_example/ :::highlight\n")
