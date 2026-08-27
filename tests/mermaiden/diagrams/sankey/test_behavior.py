import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestSankey:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_node", {"id": "grid", "label": 'Grid, "main"'}),
            DiagramCommand("add_node", {"id": "homes", "label": "Homes"}),
            DiagramCommand("add_flow", {"id": "supply", "source_id": "grid", "target_id": "homes", "value": 113.726}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("sankey").commands) == {item.operation for item in commands} | {
            "remove_element",
            "remove_relation",
        }
        assert '"Grid, \\"main\\"","Homes",113.726' in source
        assert application.render(restored) == source

    def test_rejects_non_positive_flows_duplicates_and_unknown_nodes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")
        application.apply(diagram, DiagramCommand("add_node", {"id": "grid", "label": "Grid"}))

        with pytest.raises(UnknownCommand):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_flow", {"id": "bad", "source_id": "grid", "target_id": "grid", "value": "negative"}
                ),
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_node", {"id": "grid", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand("add_flow", {"id": "missing", "source_id": "grid", "target_id": "missing", "value": 1}),
            )
