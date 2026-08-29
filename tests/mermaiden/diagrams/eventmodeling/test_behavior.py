import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestEventModeling:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("eventmodeling")

        for command in (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_swimlane", {"id": "checkout", "label": 'Check "out"'}),
            DiagramCommand("add_actor", {"id": "actor", "label": "Actor", "swimlane_id": "checkout"}),
            DiagramCommand("add_command", {"id": "command", "label": "Command", "swimlane_id": "checkout"}),
            DiagramCommand("add_event", {"id": "event", "label": "Event", "swimlane_id": "checkout"}),
            DiagramCommand("add_view", {"id": "view", "label": "View", "swimlane_id": "checkout"}),
            DiagramCommand("add_flow", {"id": "submit", "source_id": "actor", "target_id": "command"}),
        ):
            application.apply(diagram, command)

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
        for fragment in ("ui actor", "cmd command", "evt event", "rmo view"):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_commands_duplicates_and_unknown_swimlanes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("eventmodeling")
        application.apply(diagram, DiagramCommand("add_swimlane", {"id": "lane", "label": "Lane"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"unknown": True}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_swimlane", {"id": "lane", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_actor", {"id": "actor", "label": "Actor", "swimlane_id": "missing"})
            )
