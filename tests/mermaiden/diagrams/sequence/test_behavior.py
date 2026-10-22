import json

import pytest

from mermaiden import Application


class TestSequenceDiagram:
    def test_exercises_every_public_command_including_explicit_activation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        commands = (
            ("configure", {"wrap": False}),
            ("add_box", {"id": "clients_example", "label": "Clients", "color": "#eee"}),
            (
                "add_participant",
                {"id": "user_example", "label": 'User "one"', "kind": "actor", "box_id": "clients_example"},
            ),
            ("add_participant", {"id": "api_example", "label": "API", "kind": "control"}),
            ("add_participant", {"id": "worker_example", "label": "Worker", "kind": "entity", "created": True}),
            ("autonumber", {"id": "numbers_example"}),
            ("activate", {"id": "activate_api_example", "participant_id": "api_example"}),
            (
                "add_message",
                {
                    "id": "request_example",
                    "source_id": "user_example",
                    "target_id": "api_example",
                    "label": 'Call "API"',
                    "kind": "dotted",
                },
            ),
            ("control", {"id": "loop_example", "kind": "loop", "label": "retry"}),
            (
                "add_message",
                {
                    "id": "work_example",
                    "source_id": "api_example",
                    "target_id": "worker_example",
                    "label": "Work",
                    "activate": True,
                    "deactivate": True,
                },
            ),
            ("control", {"id": "end_example", "kind": "end"}),
            ("create", {"id": "create_worker_example", "participant_id": "worker_example"}),
            ("deactivate", {"id": "deactivate_api_example", "participant_id": "api_example"}),
            ("destroy", {"id": "destroy_worker_example", "participant_id": "worker_example"}),
            (
                "add_note",
                {
                    "id": "note_example",
                    "text": 'Across "both"',
                    "participant_ids": ["user_example", "api_example"],
                    "position": "over",
                },
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("sequenceDiagram").commands) == {item[0] for item in commands} | {
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
            "box #eee Clients",
            "actor user_example as User",
            "autonumber",
            "activate api_example",
            "user_example-->>api_example",
            "loop retry",
            "end",
            "create participant",
            "deactivate api_example",
            "destroy worker_example",
            "Note over user_example,api_example",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_note_cardinality_duplicates_and_unknown_participants(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sequenceDiagram")
        application.execute(diagram, "add_participant", {"id": "user_example", "label": "User"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_note", {"id": "empty_example", "text": "Empty", "participant_ids": []})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_message",
                {
                    "id": "syntax_example",
                    "source_id": "user_example",
                    "target_id": "user_example",
                    "label": "syntax_example",
                    "kind": "-->>",
                },
            )
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_note",
                {"id": "many_example", "text": "Many", "participant_ids": ["user_example", "two", "three"]},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_participant", {"id": "user_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(diagram, "activate", {"id": "bad_example", "participant_id": "missing_example"})
