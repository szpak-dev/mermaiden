import json

import pytest

from mermaiden import Application


class TestSwimlane:
    def test_exercises_every_public_command_including_flow_removal(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("swimlane-beta")
        commands = (
            ("configure", {"lineHops": "gap", "automaticLaneOrdering": True}),
            ("add_lane", {"id": "customer_example", "label": 'Customer "lane_example"'}),
            ("add_start", {"id": "start_example", "label": "Start", "lane_id": "customer_example"}),
            ("add_activity", {"id": "work_example", "label": "Work", "lane_id": "customer_example"}),
            ("add_decision", {"id": "decision_example", "label": "Done?", "lane_id": "customer_example"}),
            ("add_connector", {"id": "connector_example", "label": "Join", "lane_id": "customer_example"}),
            ("add_end", {"id": "end_example", "label": "End", "lane_id": "customer_example"}),
            (
                "add_flow",
                {"id": "start_work_example", "source_id": "start_example", "target_id": "work_example", "label": "go"},
            ),
            (
                "add_conditional_flow",
                {"id": "yes_example", "source_id": "decision_example", "target_id": "end_example", "condition": "Yes"},
            ),
            ("remove_flow", {"id": "start_work_example"}),
            ("add_flow", {"id": "work_decision_example", "source_id": "work_example", "target_id": "decision_example"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("swimlane-beta").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        for fragment in (
            "subgraph",
            'e_v_start_example(["Start"])',
            'e_v_work_example["Work"]',
            'e_v_decision_example{"Done?"}',
            'e_v_connector_example(("Join"))',
            'e_v_end_example(["End"])',
            "Yes",
        ):
            assert fragment in source
        assert "start_work_example" not in str(application.snapshot(diagram).to_dict())
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_unknown_lanes_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("swimlane-beta")
        application.execute(diagram, "add_lane", {"id": "lane_example", "label": "Lane"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"lineHops": "jump"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_lane", {"id": "lane_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_activity", {"id": "orphan_example", "label": "Orphan", "lane_id": "missing_example"}
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.execute(diagram, "remove_flow", {"id": "missing_example"})
