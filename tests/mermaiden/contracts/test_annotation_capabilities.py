import json
from pathlib import Path

import pytest

from mermaiden import Application


class TestAnnotationCapabilities:
    @pytest.mark.parametrize("kind,create", (("classDiagram", "add_class"), ("treeView-beta", "add_item")))
    @pytest.mark.parametrize("operation", ("create", "update_annotation", "remove_annotation"))
    @pytest.mark.parametrize("batch", (False, True))
    def test_removed_annotation_commands_are_rejected_without_mutating_the_diagram(
        self, kind: str, create: str, operation: str, batch: bool
    ) -> None:
        with Application.create() as application:
            diagram = application.create_diagram(kind)
            application.execute(diagram, create, {"id": "element_example", "label": "Element example"})
            if operation == "create":
                operation = "add_note" if kind == "classDiagram" else "add_annotation"
                arguments: dict[str, object] = (
                    {"id": "note_example", "class_id": "element_example", "text": "Note example"}
                    if kind == "classDiagram"
                    else {"id": "note_example", "element_id": "element_example", "highlight": True}
                )
            elif operation == "update_annotation":
                arguments = {
                    "id": "note_example",
                    "kind": "class_note" if kind == "classDiagram" else "tree_annotation",
                    "changes": {"text": "Note example"} if kind == "classDiagram" else {"highlight": True},
                }
            else:
                arguments = {"id": "note_example"}
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            with pytest.raises(RuntimeError, match=operation):
                if batch:
                    application.apply_batch(
                        diagram,
                        [
                            {"operation": create, "arguments": {"id": "pending_example", "label": "Pending example"}},
                            {"operation": operation, "arguments": arguments},
                        ],
                    )
                else:
                    application.execute(diagram, operation, arguments)
            assert application.snapshot(diagram).to_dict() == before
            assert application.render(diagram) == source
            application.execute(diagram, create, {"id": "pending_example", "label": "Pending example"})
            assert "Pending example" in application.render(diagram)

    @pytest.mark.parametrize("filename", ("class-note-v9.json", "tree-annotation-v9.json"))
    def test_legacy_annotations_require_explicit_removal_before_snapshot_migration(self, filename: str) -> None:
        path = Path(__file__).parents[2] / "fixtures" / "snapshots" / filename
        legacy = json.loads(path.read_text(encoding="utf-8"))
        with Application.create() as application:
            with pytest.raises(RuntimeError, match="version '9'; expected version '10'"):
                application.restore(legacy)
            legacy["version"] = 10
            untouched = json.dumps(legacy, sort_keys=True)
            with pytest.raises(RuntimeError, match=r"discriminator|annotation"):
                application.restore(legacy)
            assert json.dumps(legacy, sort_keys=True) == untouched
            legacy["annotations"] = []
            restored = application.restore(legacy)
            assert application.snapshot(restored).to_dict() == legacy
            source = application.render(restored)
            assert "Element example" in source
            assert "Note example" not in source
            assert ":::highlight" not in source
            assert "icon(folder)" not in source
            assert "Description example" not in source
            if legacy["kind"] == "classDiagram":
                assert "<<interface>>" in source
                assert "<<abstract>>" in source

    def test_version_nine_requires_explicit_migration_for_every_diagram_kind(self) -> None:
        with Application.create() as application:
            for info in application.available_diagrams():
                snapshot = application.snapshot(application.create_diagram(info.id)).to_dict()
                snapshot["version"] = 9
                with pytest.raises(RuntimeError, match="version '9'; expected version '10'"):
                    application.restore(snapshot)
                snapshot["version"] = 10
                assert application.snapshot(application.restore(snapshot)).to_dict() == snapshot

    @pytest.mark.parametrize("kind", ("classDiagram", "treeView-beta"))
    def test_discovery_omits_standalone_annotations_and_their_commands(self, kind: str) -> None:
        with Application.create() as application:
            description = application.diagram_description(kind)
            assert not description.annotations
            for operation in ("add_note", "add_annotation", "update_annotation", "remove_annotation"):
                assert operation not in description.commands
                with pytest.raises(KeyError, match=operation):
                    application.command_payload(kind, operation)

    def test_class_stereotypes_survive_update_and_snapshot_restore(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(
                diagram, "add_class", {"id": "class_example", "label": "Class example", "annotations": ["interface"]}
            )
            assert "<<interface>>" in application.render(diagram)
            application.execute(
                diagram,
                "update_element",
                {"id": "class_example", "kind": "class", "changes": {"annotations": ["abstract"]}},
            )
            restored = application.restore(application.snapshot(diagram).to_dict())
            assert "<<abstract>>" in application.render(restored)
            assert "<<interface>>" not in application.render(restored)
            assert application.snapshot(restored).annotations == ()
