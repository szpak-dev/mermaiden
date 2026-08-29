import json

import pytest
from contracts.mutation_conformance import assert_mutation_conformance

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestStateDiagram:
    def test_exercises_every_public_command_including_transition_removal(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("stateDiagram-v2")

        commands = (
            DiagramCommand("configure", {"defaultRenderer": "elk", "titleTopMargin": 30}),
            DiagramCommand("add_initial", {"id": "initial"}),
            DiagramCommand("add_state", {"id": "idle", "label": 'Idle "state"'}),
            DiagramCommand("add_choice", {"id": "choice", "label": "Route"}),
            DiagramCommand("add_fork", {"id": "fork", "label": "Fork"}),
            DiagramCommand("add_join", {"id": "join", "label": "Join"}),
            DiagramCommand("add_composite", {"id": "active", "label": "Active"}),
            DiagramCommand("add_state", {"id": "nested", "label": "Nested", "composite_id": "active"}),
            DiagramCommand("add_final", {"id": "final"}),
            DiagramCommand("add_transition", {"id": "start", "source_id": "initial", "target_id": "idle"}),
            DiagramCommand(
                "add_transition", {"id": "route", "source_id": "idle", "target_id": "choice", "label": "go"}
            ),
            DiagramCommand("add_note", {"id": "note", "state_id": "idle", "text": 'Wait "here"', "position": "left"}),
            DiagramCommand("remove_transition", {"id": "route"}),
            DiagramCommand(
                "add_transition", {"id": "finish", "source_id": "idle", "target_id": "final", "label": "done"}
            ),
        )
        for command in commands:
            application.apply(diagram, command)

        assert_mutation_conformance(application, application.snapshot(diagram).to_dict())
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("stateDiagram-v2").commands) == {
            item.operation for item in commands
        } | {
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
            "state s_v_active {",
            "[*] -->",
            "--> [*]",
            "note left of",
        ):
            assert fragment in source
        assert "route" not in source
        assert application.render(restored) == source

    def test_rejects_invalid_positions_duplicates_unknown_targets_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("stateDiagram-v2")
        application.apply(diagram, DiagramCommand("add_state", {"id": "idle", "label": "Idle"}))

        with pytest.raises(UnknownCommand):
            application.apply(
                diagram,
                DiagramCommand("add_note", {"id": "bad", "state_id": "idle", "text": "Bad", "position": "above"}),
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_state", {"id": "idle", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand("add_transition", {"id": "bad_transition", "source_id": "idle", "target_id": "missing"}),
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.apply(diagram, DiagramCommand("remove_transition", {"id": "missing"}))
