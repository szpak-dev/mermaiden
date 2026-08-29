import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestSwimlane:
    def test_exercises_every_public_command_including_flow_removal(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("swimlane-beta")

        commands = (
            DiagramCommand("configure", {"lineHops": "gap", "automaticLaneOrdering": True}),
            DiagramCommand("add_lane", {"id": "customer", "label": 'Customer "lane"'}),
            DiagramCommand("add_start", {"id": "start", "label": "Start", "lane_id": "customer"}),
            DiagramCommand("add_activity", {"id": "work", "label": "Work", "lane_id": "customer"}),
            DiagramCommand("add_decision", {"id": "decision", "label": "Done?", "lane_id": "customer"}),
            DiagramCommand("add_connector", {"id": "connector", "label": "Join", "lane_id": "customer"}),
            DiagramCommand("add_end", {"id": "end", "label": "End", "lane_id": "customer"}),
            DiagramCommand("add_flow", {"id": "start_work", "source_id": "start", "target_id": "work", "label": "go"}),
            DiagramCommand(
                "add_conditional_flow", {"id": "yes", "source_id": "decision", "target_id": "end", "condition": "Yes"}
            ),
            DiagramCommand("remove_flow", {"id": "start_work"}),
            DiagramCommand("add_flow", {"id": "work_decision", "source_id": "work", "target_id": "decision"}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("swimlane-beta").commands) == {
            item.operation for item in commands
        } | {"update_element", "remove_element", "update_relation", "remove_relation"}
        for fragment in (
            "subgraph",
            'e_v_start(["Start"])',
            'e_v_work["Work"]',
            'e_v_decision{"Done?"}',
            'e_v_connector(("Join"))',
            'e_v_end(["End"])',
            "Yes",
        ):
            assert fragment in source
        assert "start_work" not in str(application.snapshot(diagram).to_dict())
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_unknown_lanes_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("swimlane-beta")
        application.apply(diagram, DiagramCommand("add_lane", {"id": "lane", "label": "Lane"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"lineHops": "jump"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_lane", {"id": "lane", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_activity", {"id": "orphan", "label": "Orphan", "lane_id": "missing"})
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.apply(diagram, DiagramCommand("remove_flow", {"id": "missing"}))
