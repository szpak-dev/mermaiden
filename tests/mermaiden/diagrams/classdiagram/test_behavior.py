import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestClassDiagram:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")

        for command in (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_namespace", {"id": "domain", "label": "Domain", "comment": "Types"}),
            DiagramCommand(
                "add_class",
                {
                    "id": "animal",
                    "label": 'Animal "kind"',
                    "parent_id": "domain",
                    "attributes": [{"name": "name", "type": "String", "visibility": "+"}],
                    "methods": [{"name": "sound", "return_type": "void", "visibility": "+"}],
                    "annotations": ["abstract"],
                },
            ),
            DiagramCommand("add_class", {"id": "duck", "label": "Duck", "parent_id": "domain"}),
            DiagramCommand(
                "add_relation",
                {
                    "id": "inherits",
                    "source_id": "animal",
                    "target_id": "duck",
                    "relation_kind": "<|--",
                    "label": "extends",
                },
            ),
            DiagramCommand("add_note", {"id": "note", "class_id": "animal", "text": 'Base "type"'}),
        ):
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("classDiagram").commands) == {
            "configure",
            "add_namespace",
            "add_class",
            "add_relation",
            "add_note",
            "remove_element",
            "remove_relation",
            "remove_annotation",
        }
        assert "namespace domain" in source
        assert "abstract" in source
        assert "<|--" in source
        assert "note for animal" in source
        assert application.render(restored) == source

    def test_rejects_bad_relations_duplicate_classes_and_unknown_note_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("classDiagram")
        application.apply(diagram, DiagramCommand("add_class", {"id": "one", "label": "One"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("add_relation", {"id": "bad"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_class", {"id": "one", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(diagram, DiagramCommand("add_note", {"id": "note", "class_id": "missing", "text": "No"}))
