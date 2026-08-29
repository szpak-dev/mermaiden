import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestPie:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("pie")

        commands = (
            DiagramCommand("configure", {"donutHole": 0.4, "legendPosition": "top"}),
            DiagramCommand("set_title", {"title": 'Adopted "pets"'}),
            DiagramCommand("show_values", {}),
            DiagramCommand("add_slice", {"id": "dogs", "label": 'Dogs "large"', "value": 386}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("pie").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
        }
        assert "pie showData" in source
        assert 'title "Adopted \\"pets\\""' in source
        assert '"Dogs \\"large\\"" : 386' in source
        assert application.render(restored) == source

    def test_rejects_invalid_values_duplicate_ids_and_bad_configuration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("pie")
        application.apply(diagram, DiagramCommand("add_slice", {"id": "dogs", "label": "Dogs", "value": 1}))

        with pytest.raises(RuntimeError, match=r"greater than zero"):
            application.apply(diagram, DiagramCommand("add_slice", {"id": "bad", "label": "Bad", "value": -1}))
        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"legendPosition": "side"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_slice", {"id": "dogs", "label": "Again", "value": 2}))
