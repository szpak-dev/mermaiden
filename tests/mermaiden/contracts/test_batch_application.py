from collections.abc import Mapping
from typing import cast

import pytest

from mermaiden import Application


class TestBatchApplication:
    def test_rejects_a_command_without_a_string_operation_before_mutation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(ValueError, match="Batch command 0 must provide a string operation"):
            application.apply_batch(diagram, ({"operation": 1, "arguments": {}},))

        assert application.snapshot(diagram).to_dict() == before

    def test_rejects_a_command_without_mapping_arguments_before_mutation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(ValueError, match="Batch command 0 must provide mapping arguments"):
            application.apply_batch(diagram, ({"operation": "add_block", "arguments": []},))

        assert application.snapshot(diagram).to_dict() == before

    def test_rolls_back_an_unknown_operation(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="Command 'missing' is not supported"):
            application.apply_batch(diagram, ({"operation": "missing", "arguments": {}},))

        assert application.snapshot(diagram).to_dict() == before

    def test_rolls_back_an_invalid_command_payload(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="'add_block' has invalid arguments"):
            application.apply_batch(
                diagram,
                ({"operation": "add_block", "arguments": {"id": "missing_label"}},),
            )

        assert application.snapshot(diagram).to_dict() == before

    def test_rolls_back_configuration_properties_and_elements_after_operation_failure(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.execute(diagram, "add_block", {"id": "original", "label": "Original"})
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="does not exist"):
            application.apply_batch(
                diagram,
                (
                    {"operation": "configure", "arguments": {"padding": 12}},
                    {"operation": "set_columns", "arguments": {"columns": 4}},
                    {"operation": "add_block", "arguments": {"id": "new", "label": "New"}},
                    {
                        "operation": "add_block",
                        "arguments": {"id": "orphan", "label": "Orphan", "parent_id": "missing"},
                    },
                ),
            )

        assert application.snapshot(diagram).to_dict() == before

    def test_rolls_back_a_batch_whose_final_state_is_invalid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        before = application.snapshot(diagram).to_dict()

        with pytest.raises(RuntimeError, match="Cannot apply batch"):
            application.apply_batch(
                diagram,
                ({"operation": "add_start", "arguments": {"id": "start", "label": "Start"}},),
            )

        assert application.snapshot(diagram).to_dict() == before

    def test_empty_batch_preserves_an_invalid_draft(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("flowchart")
        before = application.snapshot(diagram).to_dict()

        report = application.apply_batch(diagram, ())

        assert not report.can_commit
        assert application.snapshot(diagram).to_dict() == before

    def test_applies_large_batches_and_round_trips_the_result(self) -> None:
        application = Application.create()

        for command_count in (100, 500, 1000):
            diagram = application.create_diagram("block")
            commands: tuple[Mapping[str, object], ...] = tuple(
                {
                    "operation": "add_block",
                    "arguments": {"id": f"block_{index}", "label": f"Block {index}"},
                }
                for index in range(command_count)
            )

            report = application.apply_batch(diagram, commands)
            snapshot = application.snapshot(diagram).to_dict()
            restored = application.restore(snapshot)
            elements = cast(list[object], snapshot["elements"])

            assert report.can_commit
            assert len(elements) == command_count
            assert application.render(restored) == application.render(diagram)
