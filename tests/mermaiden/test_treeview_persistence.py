import json
from collections.abc import Mapping
from typing import cast

from mermaiden.application import Application, DiagramCommand


class TestTreeViewPersistence:
    def test_uses_branches_as_the_only_public_nesting_operation(self) -> None:
        application = Application.create()
        schema = application.command_payload("treeView-beta", "add_item").model_json_schema()

        assert "parent_id" not in schema["properties"]

    def test_preserves_addressability_through_incremental_branches_and_annotations(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        revisions = (
            DiagramCommand("add_item", {"id": "example_root", "label": "root/"}),
            DiagramCommand("add_item", {"id": "example_child_one", "label": "child-one/"}),
            DiagramCommand("add_item", {"id": "example_child_two", "label": "child-two/"}),
            DiagramCommand("add_item", {"id": "example_grandchild", "label": "leaf.txt"}),
            DiagramCommand(
                "add_annotation",
                {"id": "before_branch", "element_id": "example_child_one", "icon": "folder"},
            ),
            DiagramCommand(
                "add_branch",
                {"id": "first_sibling", "parent_id": "example_root", "child_id": "example_child_one"},
            ),
            DiagramCommand(
                "add_branch",
                {"id": "second_sibling", "parent_id": "example_root", "child_id": "example_child_two"},
            ),
            DiagramCommand(
                "add_annotation",
                {"id": "after_branch", "element_id": "example_child_two", "description": "Second child"},
            ),
            DiagramCommand(
                "add_branch",
                {"id": "nested", "parent_id": "example_child_one", "child_id": "example_grandchild"},
            ),
            DiagramCommand(
                "add_annotation",
                {"id": "after_nested_branch", "element_id": "example_grandchild", "highlight": True},
            ),
        )
        expected_ids: set[str] = set()
        source = ""

        for command in revisions:
            report = application.apply(diagram, command)
            if command.operation == "add_item":
                expected_ids.add(cast(str, command.arguments["id"]))
            snapshot = application.snapshot(diagram).to_dict()
            persisted_ids = {
                cast(str, cast(Mapping[str, object], cast(Mapping[str, object], element)["fields"])["id"])
                for element in cast(list[object], snapshot["elements"])
            }
            diagram = application.restore(json.loads(json.dumps(snapshot)))
            source = application.render(diagram)

            assert report is not None
            assert report.accepted
            assert persisted_ids == expected_ids
            assert source.startswith("---\nconfig:\n  wrap: true\n---\ntreeView-beta\n")

        assert source.endswith(
            "treeView-beta\nroot/\n  child-one/ icon(folder)\n"
            "    leaf.txt :::highlight\n  child-two/ ## Second child\n"
        )
