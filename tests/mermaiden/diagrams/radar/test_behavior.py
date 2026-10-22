import json

import pytest

from mermaiden import Application


class TestRadar:
    def test_exercises_every_public_command_including_legend_and_restores_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("radar-beta")
        commands = (
            ("configure", {"width": 720, "curveTension": 0.25}),
            ("set_title", {"title": 'Quality "comparison"'}),
            ("add_axis", {"id": "speed_example", "label": "Speed"}),
            ("add_axis", {"id": "quality_example", "label": "Quality"}),
            ("add_curve", {"id": "one_example", "label": "Option one_example", "values": [4, 3]}),
            ("set_range", {"minimum": 0, "maximum": 5}),
            ("set_graticule", {"graticule": "polygon"}),
            ("set_ticks", {"ticks": 5}),
            ("set_legend", {"visible": False}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("radar-beta").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        for fragment in (
            'title Quality "comparison"',
            'axis speed_example["Speed"], quality_example["Quality"]',
            'curve one_example["Option one_example"]{ 4, 3 }',
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
        application.execute(diagram, "add_axis", {"id": "speed_example", "label": "Speed"})
        application.execute(diagram, "add_axis", {"id": "quality_example", "label": "Quality"})
        with pytest.raises(RuntimeError, match=r"values|axes|cardinality"):
            application.execute(diagram, "add_curve", {"id": "bad_example", "label": "Bad", "values": [1]})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "set_ticks", {"ticks": "many"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_axis", {"id": "speed_example", "label": "Again"})
