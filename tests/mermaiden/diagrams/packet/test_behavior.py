import json

import pytest

from mermaiden import Application


class TestPacket:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("packet")
        commands = (
            ("configure", {"bitsPerRow": 16, "showBits": False}),
            ("set_title", {"title": 'UDP "packet"'}),
            ("add_bits", {"id": "source_example", "label": "Source port", "bits": 16}),
            ("add_field", {"id": "length_example", "label": "Length", "start": 16, "end": 31}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("packet").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'title UDP "packet"' in source
        assert '+16: "Source port"' in source
        assert '16-31: "Length"' in source
        assert application.render(restored) == source

    def test_rejects_invalid_ranges_duplicates_and_non_positive_bit_counts(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("packet")
        application.execute(diagram, "add_bits", {"id": "field_example", "label": "Field", "bits": 8})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_bits", {"id": "bad_example", "label": "Bad", "bits": "many"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_field", {"id": "range_example", "label": "Range", "start": "eight"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_bits", {"id": "field_example", "label": "Again", "bits": 8})

    @pytest.mark.parametrize(
        "changes",
        (
            {"start": 32, "end": 47},
            {"bits": 16},
            {"position": {"kind": "bits", "bits": 0}},
            {"position": {"kind": "bits", "bits": 8, "start": 0}},
            {"position": {"kind": "range", "start": -1, "end": 7}},
            {"position": {"kind": "range", "start": 8, "end": 7}},
            {"position": {"kind": "range", "start": 0}},
            {"position": {"kind": "example", "bits": 8}},
        ),
    )
    def test_rejects_ambiguous_or_invalid_position_updates_atomically(self, changes: dict[str, object]) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("packet")
            application.execute(diagram, "add_field", {"id": "field_example", "label": "Header example", "start": 0})
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(RuntimeError):
                application.execute(
                    diagram, "update_element", {"id": "field_example", "kind": "packet_field", "changes": changes}
                )
            assert application.snapshot(diagram).to_dict() == before
            assert '0: "Header example"' in application.render(diagram)
            application.execute(
                diagram,
                "update_element",
                {"id": "field_example", "kind": "packet_field", "changes": {"position": {"kind": "bits", "bits": 16}}},
            )
            assert '+16: "Header example"' in application.render(diagram)

    def test_switches_complete_positions_and_round_trips_the_selected_mode(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("packet")
            application.execute(
                diagram, "add_field", {"id": "field_example", "label": "Header example", "start": 0, "end": 7}
            )
            for position, expected in (
                ({"kind": "bits", "bits": 16}, '+16: "Header example"'),
                ({"kind": "range", "start": 32, "end": 47}, '32-47: "Header example"'),
                ({"kind": "range", "start": 0, "end": 0}, '0: "Header example"'),
            ):
                application.execute(
                    diagram,
                    "update_element",
                    {"id": "field_example", "kind": "packet_field", "changes": {"position": position}},
                )
                snapshot = application.snapshot(diagram).to_dict()
                assert snapshot["version"] == 12
                restored = application.restore(json.loads(json.dumps(snapshot)))
                assert application.render(restored).split("packet\n")[-1].strip() == expected
                assert application.snapshot(restored).to_dict() == snapshot

    @pytest.mark.parametrize(
        ("command", "arguments"),
        (
            ("add_bits", {"bits": 0}),
            ("add_bits", {"bits": -1}),
            ("add_field", {"start": -1}),
            ("add_field", {"start": 8, "end": 7}),
        ),
    )
    def test_rejects_invalid_position_creation_at_the_public_boundary(
        self, command: str, arguments: dict[str, object]
    ) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("packet")
            before = application.snapshot(diagram).to_dict()
            with pytest.raises(RuntimeError):
                application.execute(diagram, command, {"id": "field_example", "label": "Field example", **arguments})
            assert application.snapshot(diagram).to_dict() == before
            application.execute(diagram, "add_bits", {"id": "field_example", "label": "Field example", "bits": 1})
            assert '+1: "Field example"' in application.render(diagram)
