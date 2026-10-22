import json

import pytest

from mermaiden import Application


class TestEventModeling:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("eventmodeling")
        for command in (
            ("configure", {"wrap": False}),
            ("add_swimlane", {"id": "checkout_example", "label": 'Check "out"'}),
            ("add_actor", {"id": "actor_example", "label": "Actor", "swimlane_id": "checkout_example"}),
            ("add_command", {"id": "command_example", "label": "Command", "swimlane_id": "checkout_example"}),
            ("add_event", {"id": "event_example", "label": "Event", "swimlane_id": "checkout_example"}),
            ("add_view", {"id": "view_example", "label": "View", "swimlane_id": "checkout_example"}),
            ("add_flow", {"id": "submit_example", "source_id": "actor_example", "target_id": "command_example"}),
        ):
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("eventmodeling").commands) == {
            "configure",
            "add_swimlane",
            "add_actor",
            "add_command",
            "add_event",
            "add_view",
            "add_flow",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        for fragment in ("ui actor_example", "cmd command_example", "evt event_example", "rmo view_example"):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_commands_duplicates_and_unknown_swimlanes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("eventmodeling")
        application.execute(diagram, "add_swimlane", {"id": "lane_example", "label": "Lane"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"unknown": True})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_swimlane", {"id": "lane_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_actor", {"id": "actor_example", "label": "Actor", "swimlane_id": "missing"}
            )
