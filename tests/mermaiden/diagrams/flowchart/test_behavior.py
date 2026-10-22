import json

import pytest

from mermaiden import Application


class TestFlowchart:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        commands = (
            ("configure", {"wrap": False}),
            ("add_group", {"id": "group_example", "label": "Group", "direction": "LR"}),
            ("add_start", {"id": "start_example", "label": "Start", "parent_id": "group_example"}),
            ("add_action", {"id": "action_example", "label": 'Act "now"', "parent_id": "group_example"}),
            ("add_decision", {"id": "decision_example", "label": "Decide", "parent_id": "group_example"}),
            ("add_data_store", {"id": "data_example", "label": "Data"}),
            ("add_document", {"id": "document_example", "label": "Document"}),
            ("add_end", {"id": "end_example", "label": "End"}),
            ("add_input_output", {"id": "io_example", "label": "I/O"}),
            ("add_junction", {"id": "junction_example", "label": "Junction"}),
            ("add_node", {"id": "node_example", "label": "Node"}),
            ("add_subprocess", {"id": "subprocess_example", "label": "Subprocess"}),
            (
                "add_flow",
                {"id": "plain_example", "source_id": "start_example", "target_id": "action_example", "label": "go"},
            ),
            ("remove_flow", {"id": "plain_example"}),
            ("add_flow", {"id": "start_action_example", "source_id": "start_example", "target_id": "action_example"}),
            (
                "add_flow",
                {"id": "action_decision_example", "source_id": "action_example", "target_id": "decision_example"},
            ),
            (
                "add_conditional_flow",
                {
                    "id": "yes_example",
                    "source_id": "decision_example",
                    "target_id": "data_example",
                    "condition": "yes_example",
                },
            ),
            (
                "add_conditional_flow",
                {
                    "id": "no_example",
                    "source_id": "decision_example",
                    "target_id": "io_example",
                    "condition": "no_example",
                },
            ),
            ("add_flow", {"id": "data_document_example", "source_id": "data_example", "target_id": "document_example"}),
            (
                "add_flow",
                {"id": "document_junction_example", "source_id": "document_example", "target_id": "junction_example"},
            ),
            ("add_flow", {"id": "io_junction_example", "source_id": "io_example", "target_id": "junction_example"}),
            ("add_flow", {"id": "junction_node_example", "source_id": "junction_example", "target_id": "node_example"}),
            (
                "add_flow",
                {"id": "node_subprocess_example", "source_id": "node_example", "target_id": "subprocess_example"},
            ),
            (
                "add_flow",
                {"id": "subprocess_end_example", "source_id": "subprocess_example", "target_id": "end_example"},
            ),
            (
                "add_note",
                {"id": "note_example", "text": 'Use "care"', "element_ids": ["action_example", "decision_example"]},
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("flowchart").commands) == {item[0] for item in commands} | {
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
            "subgraph",
            "shape: circle",
            "shape: rect",
            "shape: diam",
            "shape: cyl",
            "shape: doc",
            "shape: dbl-circ",
            "shape: lean-r",
            "shape: f-circ",
        ):
            assert fragment in source
        assert 'e_v_start_example -->|"go"| e_v_action_example' not in source
        assert "yes_example" in source
        assert application.render(restored) == source

    def test_rejects_invalid_arguments_duplicates_and_unknown_flow_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_group", {"id": "bad_example", "label": "Bad", "direction": "SIDEWAYS"})
        application.execute(diagram, "add_start", {"id": "start_example", "label": "Start"})
        application.execute(diagram, "add_end", {"id": "end_example", "label": "End"})
        application.execute(
            diagram, "add_flow", {"id": "path_example", "source_id": "start_example", "target_id": "end_example"}
        )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_end", {"id": "end_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_flow",
                {"id": "flow_example", "source_id": "start_example", "target_id": "missing_example"},
            )
