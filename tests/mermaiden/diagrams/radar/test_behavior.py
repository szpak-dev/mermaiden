import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestRadar:
    def test_exercises_every_public_command_including_legend_and_restores_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("radar-beta")

        commands = (
            DiagramCommand("configure", {"width": 720, "curveTension": 0.25}),
            DiagramCommand("set_title", {"title": 'Quality "comparison"'}),
            DiagramCommand("add_axis", {"id": "speed", "label": "Speed"}),
            DiagramCommand("add_axis", {"id": "quality", "label": "Quality"}),
            DiagramCommand("add_curve", {"id": "one", "label": "Option one", "values": [4, 3]}),
            DiagramCommand("set_range", {"minimum": 0, "maximum": 5}),
            DiagramCommand("set_graticule", {"graticule": "polygon"}),
            DiagramCommand("set_ticks", {"ticks": 5}),
            DiagramCommand("set_legend", {"visible": False}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("radar-beta").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
        }
        for fragment in (
            'title Quality "comparison"',
            'axis speed["Speed"], quality["Quality"]',
            'curve one["Option one"]{ 4, 3 }',
            "showLegend false",
            "max 5",
            "min 0",
            "graticule polygon",
            "ticks 5",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_curve_cardinality_invalid_ranges_and_duplicate_axes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("radar-beta")
        application.apply(diagram, DiagramCommand("add_axis", {"id": "speed", "label": "Speed"}))
        application.apply(diagram, DiagramCommand("add_axis", {"id": "quality", "label": "Quality"}))

        with pytest.raises(RuntimeError, match=r"values|axes|cardinality"):
            application.apply(diagram, DiagramCommand("add_curve", {"id": "bad", "label": "Bad", "values": [1]}))
        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("set_ticks", {"ticks": "many"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_axis", {"id": "speed", "label": "Again"}))
