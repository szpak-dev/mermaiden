import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestPacket:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("packet")

        commands = (
            DiagramCommand("configure", {"bitsPerRow": 16, "showBits": False}),
            DiagramCommand("set_title", {"title": 'UDP "packet"'}),
            DiagramCommand("add_bits", {"id": "source", "label": "Source port", "bits": 16}),
            DiagramCommand("add_field", {"id": "length", "label": "Length", "start": 16, "end": 31}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("packet").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
        }
        assert 'title UDP "packet"' in source
        assert '+16: "Source port"' in source
        assert '16-31: "Length"' in source
        assert application.render(restored) == source

    def test_rejects_invalid_ranges_duplicates_and_non_positive_bit_counts(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("packet")
        application.apply(diagram, DiagramCommand("add_bits", {"id": "field", "label": "Field", "bits": 8}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("add_bits", {"id": "bad", "label": "Bad", "bits": "many"}))
        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("add_field", {"id": "range", "label": "Range", "start": "eight"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_bits", {"id": "field", "label": "Again", "bits": 8}))
