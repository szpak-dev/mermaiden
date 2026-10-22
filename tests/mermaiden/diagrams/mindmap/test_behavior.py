import json

import pytest

from mermaiden import Application


class TestMindmap:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("mindmap")
        commands = (
            ("configure", {"padding": 12, "maxNodeWidth": 180}),
            ("add_root", {"id": "root_example", "label": 'Root "map"'}),
            ("add_node", {"id": "node_example", "label": "Node", "parent_id": "root_example"}),
            ("add_square", {"id": "square_example", "label": "Square", "parent_id": "root_example"}),
            ("add_rounded_square", {"id": "rounded_example", "label": "Rounded", "parent_id": "root_example"}),
            ("add_circle", {"id": "circle_example", "label": "Circle", "parent_id": "root_example"}),
            ("add_bang", {"id": "bang_example", "label": "Bang", "parent_id": "root_example"}),
            ("add_cloud", {"id": "cloud_example", "label": "Cloud", "parent_id": "root_example"}),
            ("add_hexagon", {"id": "hexagon_example", "label": "Hexagon", "parent_id": "root_example"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("mindmap").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        for fragment in ('["Square"]', '("Rounded")', '(("Circle"))', '))"Bang"((', ')"Cloud"(', '{{"Hexagon"}}'):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicate_roots_and_unknown_parents(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("mindmap")
        application.execute(diagram, "add_root", {"id": "root_example", "label": "Root"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"padding": "wide"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_root", {"id": "other_example", "label": "Other"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_node", {"id": "orphan_example", "label": "Orphan", "parent_id": "missing_example"}
            )
