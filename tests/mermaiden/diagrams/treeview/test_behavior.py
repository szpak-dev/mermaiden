import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestTreeView:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_item", {"id": "root", "label": "root/"}),
            DiagramCommand("add_item", {"id": "child", "label": 'child "one"'}),
            DiagramCommand("add_branch", {"id": "branch", "parent_id": "root", "child_id": "child"}),
            DiagramCommand(
                "add_annotation",
                {
                    "id": "annotation",
                    "element_id": "child",
                    "highlight": True,
                    "icon": "folder",
                    "description": "Docs",
                },
            ),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("treeView-beta").commands) == {item.operation for item in commands}
        assert '"child \\"one\\"" :::highlight icon(folder) ## Docs' in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_and_unknown_annotation_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("treeView-beta")
        application.apply(diagram, DiagramCommand("add_item", {"id": "root", "label": "root/"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"missing": True}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_item", {"id": "root", "label": "again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_annotation",
                    {"id": "annotation", "element_id": "missing", "description": "Missing"},
                ),
            )
