import json

import pytest

from mermaiden import Application


class TestPie:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("pie")
        application.execute(diagram, "configure", {"donutHole": 0.4, "legendPosition": "top"})
        application.execute(diagram, "set_title", {"title": 'Adopted "pets"'})
        application.execute(diagram, "show_values", {})
        application.execute(diagram, "add_slice", {"id": "dogs_example", "label": 'Dogs "large"', "value": 386})
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("pie").commands) == {
            "configure",
            "set_title",
            "show_values",
            "add_slice",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert "pie showData" in source
        assert 'title "Adopted \\"pets\\""' in source
        assert '"Dogs \\"large\\"" : 386' in source
        assert application.render(restored) == source

    def test_rejects_invalid_values_duplicate_ids_and_bad_configuration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("pie")
        application.execute(diagram, "add_slice", {"id": "dogs_example", "label": "Dogs", "value": 1})
        with pytest.raises(RuntimeError, match=r"greater than zero"):
            application.execute(diagram, "add_slice", {"id": "bad_example", "label": "Bad", "value": -1})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"legendPosition": "side"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_slice", {"id": "dogs_example", "label": "Again", "value": 2})
