import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestMindmap:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("mindmap")

        commands = (
            DiagramCommand("configure", {"padding": 12, "maxNodeWidth": 180}),
            DiagramCommand("add_root", {"id": "root", "label": 'Root "map"'}),
            DiagramCommand("add_node", {"id": "node", "label": "Node", "parent_id": "root"}),
            DiagramCommand("add_square", {"id": "square", "label": "Square", "parent_id": "root"}),
            DiagramCommand("add_rounded_square", {"id": "rounded", "label": "Rounded", "parent_id": "root"}),
            DiagramCommand("add_circle", {"id": "circle", "label": "Circle", "parent_id": "root"}),
            DiagramCommand("add_bang", {"id": "bang", "label": "Bang", "parent_id": "root"}),
            DiagramCommand("add_cloud", {"id": "cloud", "label": "Cloud", "parent_id": "root"}),
            DiagramCommand("add_hexagon", {"id": "hexagon", "label": "Hexagon", "parent_id": "root"}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("mindmap").commands) == {item.operation for item in commands} | {
            "remove_element"
        }
        for fragment in ('["Square"]', '("Rounded")', '(("Circle"))', '))"Bang"((', ')"Cloud"(', '{{"Hexagon"}}'):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicate_roots_and_unknown_parents(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("mindmap")
        application.apply(diagram, DiagramCommand("add_root", {"id": "root", "label": "Root"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"padding": "wide"}))
        with pytest.raises(RuntimeError):
            application.apply(diagram, DiagramCommand("add_root", {"id": "other", "label": "Other"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_node", {"id": "orphan", "label": "Orphan", "parent_id": "missing"})
            )
