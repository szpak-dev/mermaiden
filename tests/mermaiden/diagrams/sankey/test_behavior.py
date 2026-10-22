import json

import pytest

from mermaiden import Application


class TestSankey:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")
        commands = (
            ("configure", {"wrap": False}),
            ("add_node", {"id": "grid_example", "label": 'Grid, "main"'}),
            ("add_node", {"id": "homes_example", "label": "Homes"}),
            (
                "add_flow",
                {"id": "supply_example", "source_id": "grid_example", "target_id": "homes_example", "value": 113.726},
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("sankey").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert '"Grid, \\"main\\"","Homes",113.726' in source
        assert application.render(restored) == source

    def test_rejects_non_positive_flows_duplicates_and_unknown_nodes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")
        application.execute(diagram, "add_node", {"id": "grid_example", "label": "Grid"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_flow",
                {"id": "bad_example", "source_id": "grid_example", "target_id": "grid_example", "value": "negative"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_node", {"id": "grid_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_flow",
                {"id": "missing_example", "source_id": "grid_example", "target_id": "missing_example", "value": 1},
            )
