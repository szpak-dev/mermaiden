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
