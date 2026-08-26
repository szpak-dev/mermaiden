import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestSequenceDiagram:
    def test_exercises_every_public_command_including_explicit_activation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_box", {"id": "clients", "label": "Clients", "color": "#eee"}),
            DiagramCommand(
                "add_participant", {"id": "user", "label": 'User "one"', "kind": "actor", "box_id": "clients"}
            ),
            DiagramCommand("add_participant", {"id": "api", "label": "API", "kind": "control"}),
            DiagramCommand("add_participant", {"id": "worker", "label": "Worker", "kind": "entity", "created": True}),
            DiagramCommand("autonumber", {"id": "numbers"}),
            DiagramCommand("activate", {"id": "activate_api", "participant_id": "api"}),
            DiagramCommand(
                "add_message",
                {"id": "request", "source_id": "user", "target_id": "api", "label": 'Call "API"', "kind": "-->>"},
            ),
            DiagramCommand("control", {"id": "loop", "kind": "loop", "label": "retry"}),
            DiagramCommand(
                "add_message",
                {
                    "id": "work",
                    "source_id": "api",
                    "target_id": "worker",
                    "label": "Work",
                    "activate": True,
                    "deactivate": True,
                },
            ),
            DiagramCommand("control", {"id": "end", "kind": "end"}),
            DiagramCommand("create", {"id": "create_worker", "participant_id": "worker"}),
            DiagramCommand("deactivate", {"id": "deactivate_api", "participant_id": "api"}),
            DiagramCommand("destroy", {"id": "destroy_worker", "participant_id": "worker"}),
            DiagramCommand(
                "add_note",
                {"id": "note", "text": 'Across "both"', "participant_ids": ["user", "api"], "position": "over"},
            ),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("sequenceDiagram").commands) == {item.operation for item in commands}
        for fragment in (
            "box #eee Clients",
            "actor user as User",
            "autonumber",
            "activate api",
            "user-->>api",
            "loop retry",
            "end",
            "create participant",
            "deactivate api",
            "destroy worker",
            "Note over user,api",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_note_cardinality_duplicates_and_unknown_participants(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.apply(diagram, DiagramCommand("add_participant", {"id": "user", "label": "User"}))

        with pytest.raises(UnknownCommand):
            application.apply(
                diagram, DiagramCommand("add_note", {"id": "empty", "text": "Empty", "participant_ids": []})
            )
        with pytest.raises(UnknownCommand):
            application.apply(
                diagram,
                DiagramCommand("add_note", {"id": "many", "text": "Many", "participant_ids": ["user", "two", "three"]}),
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_participant", {"id": "user", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(diagram, DiagramCommand("activate", {"id": "bad", "participant_id": "missing"}))
