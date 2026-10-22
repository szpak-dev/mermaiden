import json

import pytest

from mermaiden import Application


class TestStateDiagram:
    def test_exercises_every_public_command_including_transition_removal(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("stateDiagram-v2")
        commands = (
            ("configure", {"layout": "elk", "titleTopMargin": 30}),
            ("add_initial", {"id": "initial_example"}),
            ("add_state", {"id": "idle_example", "label": 'Idle "state"'}),
            ("add_choice", {"id": "choice_example", "label": "Route"}),
            ("add_fork", {"id": "fork_example", "label": "Fork"}),
            ("add_join", {"id": "join_example", "label": "Join"}),
            ("add_composite", {"id": "active_example", "label": "Active"}),
            ("add_state", {"id": "nested_example", "label": "Nested", "composite_id": "active_example"}),
            ("add_final", {"id": "final_example"}),
            ("add_transition", {"id": "start_example", "source_id": "initial_example", "target_id": "idle_example"}),
            (
                "add_transition",
                {"id": "route_example", "source_id": "idle_example", "target_id": "choice_example", "label": "go"},
            ),
            ("add_note", {"id": "note_example", "state_id": "idle_example", "text": 'Wait "here"', "position": "left"}),
            ("remove_transition", {"id": "route_example"}),
            (
                "add_transition",
                {"id": "finish_example", "source_id": "idle_example", "target_id": "final_example", "label": "done"},
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        body = source.split("---\n", maxsplit=2)[2]
        assert body.splitlines()[:2] == ["stateDiagram-v2", "direction TB"]
        assert "stateDiagram-v2 TD" not in source
        assert set(application.diagram_description("stateDiagram-v2").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
            "update_annotation",
            "remove_annotation",
        }
        for fragment in (
            'state "Idle \\"state\\""',
            "<<choice>>",
            "<<fork>>",
            "<<join>>",
            "state s_v_active_example {",
            "[*] -->",
            "--> [*]",
            "note left of",
        ):
            assert fragment in source
        assert "route_example" not in source
        assert application.render(restored) == source

    def test_rejects_invalid_positions_duplicates_unknown_targets_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("stateDiagram-v2")
        application.execute(diagram, "add_state", {"id": "idle_example", "label": "Idle"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_note",
                {"id": "bad_example", "state_id": "idle_example", "text": "Bad", "position": "above"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_state", {"id": "idle_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_transition",
                {"id": "bad_transition_example", "source_id": "idle_example", "target_id": "missing_example"},
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.execute(diagram, "remove_transition", {"id": "missing_example"})
