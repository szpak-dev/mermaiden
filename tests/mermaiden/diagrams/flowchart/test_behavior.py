import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestFlowchart:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_group", {"id": "group", "label": "Group", "direction": "LR"}),
            DiagramCommand("add_start", {"id": "start", "label": "Start", "parent_id": "group"}),
            DiagramCommand("add_action", {"id": "action", "label": 'Act "now"', "parent_id": "group"}),
            DiagramCommand("add_decision", {"id": "decision", "label": "Decide", "parent_id": "group"}),
            DiagramCommand("add_data_store", {"id": "data", "label": "Data"}),
            DiagramCommand("add_document", {"id": "document", "label": "Document"}),
            DiagramCommand("add_end", {"id": "end", "label": "End"}),
            DiagramCommand("add_input_output", {"id": "io", "label": "I/O"}),
            DiagramCommand("add_junction", {"id": "junction", "label": "Junction"}),
            DiagramCommand("add_node", {"id": "node", "label": "Node"}),
            DiagramCommand("add_subprocess", {"id": "subprocess", "label": "Subprocess"}),
            DiagramCommand("add_flow", {"id": "plain", "source_id": "start", "target_id": "action", "label": "go"}),
            DiagramCommand("remove_flow", {"id": "plain"}),
            DiagramCommand("add_flow", {"id": "start_action", "source_id": "start", "target_id": "action"}),
            DiagramCommand("add_flow", {"id": "action_decision", "source_id": "action", "target_id": "decision"}),
            DiagramCommand(
                "add_conditional_flow",
                {"id": "yes", "source_id": "decision", "target_id": "data", "condition": "yes"},
            ),
            DiagramCommand(
                "add_conditional_flow",
                {"id": "no", "source_id": "decision", "target_id": "io", "condition": "no"},
            ),
            DiagramCommand("add_flow", {"id": "data_document", "source_id": "data", "target_id": "document"}),
            DiagramCommand("add_flow", {"id": "document_junction", "source_id": "document", "target_id": "junction"}),
            DiagramCommand("add_flow", {"id": "io_junction", "source_id": "io", "target_id": "junction"}),
            DiagramCommand("add_flow", {"id": "junction_node", "source_id": "junction", "target_id": "node"}),
            DiagramCommand("add_flow", {"id": "node_subprocess", "source_id": "node", "target_id": "subprocess"}),
            DiagramCommand("add_flow", {"id": "subprocess_end", "source_id": "subprocess", "target_id": "end"}),
            DiagramCommand("add_note", {"id": "note", "text": 'Use "care"', "element_ids": ["action", "decision"]}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("flowchart").commands) == {item.operation for item in commands} | {
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
        assert 'e_v_start -->|"go"| e_v_action' not in source
        assert "yes" in source
        assert application.render(restored) == source

    def test_rejects_invalid_arguments_duplicates_and_unknown_flow_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        with pytest.raises(UnknownCommand):
            application.apply(
                diagram, DiagramCommand("add_group", {"id": "bad", "label": "Bad", "direction": "SIDEWAYS"})
            )
        application.apply(diagram, DiagramCommand("add_start", {"id": "start", "label": "Start"}))
        application.apply(diagram, DiagramCommand("add_end", {"id": "end", "label": "End"}))
        application.apply(diagram, DiagramCommand("add_flow", {"id": "path", "source_id": "start", "target_id": "end"}))

        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_end", {"id": "end", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_flow", {"id": "flow", "source_id": "start", "target_id": "missing"})
            )
