import re
from xml.etree import ElementTree

import pytest

from mermaiden import Application


class TestClassLayout:
    @pytest.mark.parametrize("layout", (None, "dagre", "elk"))
    def test_layout_defaults_to_elk_and_preserves_explicit_choices_through_restore(self, layout: str | None) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            application.execute(diagram, "add_class", {"id": "class_example", "label": "Class example"})
            if layout is not None:
                application.execute(diagram, "configure", {"layout": layout})
            source = application.render(diagram)
            assert f'"layout": "{layout or "elk"}"' in source
            assert '"theme": "redux-color"' in source
            assert '"look": "neo"' in source
            assert '"htmlLabels": false' in source
            assert '"hierarchicalNamespaces": true' in source
            restored = application.restore(application.snapshot(diagram).to_dict())
            assert application.render(restored) == source

    @pytest.mark.integration
    def test_default_layout_routes_relations_with_orthogonal_segments(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("classDiagram")
            for name in ("root_example", "left_example", "right_example", "leaf_example"):
                application.execute(diagram, "add_class", {"id": name, "label": name})
            for index, (source, target) in enumerate(
                (
                    ("root_example", "left_example"),
                    ("root_example", "right_example"),
                    ("left_example", "leaf_example"),
                    ("right_example", "leaf_example"),
                    ("root_example", "leaf_example"),
                )
            ):
                application.execute(
                    diagram,
                    "add_relation",
                    {"id": f"relation_example_{index}", "source_id": source, "target_id": target},
                )
            before = application.snapshot(diagram).to_dict()
            report = application.validate_render(diagram)
            assert report.success, report.diagnostics
            svg = ElementTree.fromstring(report.svg)
            paths = [
                element
                for element in svg.iter("{http://www.w3.org/2000/svg}path")
                if "relation" in element.attrib.get("class", "").split()
            ]
            assert len(paths) == 5
            horizontal = vertical = 0
            for path in paths:
                commands = re.findall(r"([A-Za-z])([^A-Za-z]*)", path.attrib["d"])
                previous: tuple[float, float] | None = None
                for command, arguments in commands:
                    assert command in {"M", "L", "Q", "A"}, path.attrib["d"]
                    values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", arguments)]
                    endpoint = (values[-2], values[-1])
                    if command == "L" and previous is not None:
                        dx, dy = abs(endpoint[0] - previous[0]), abs(endpoint[1] - previous[1])
                        assert dx < 0.01 or dy < 0.01, path.attrib["d"]
                        horizontal += int(dx > 0.01)
                        vertical += int(dy > 0.01)
                    previous = endpoint
            assert horizontal > 0
            assert vertical > 0
            assert application.snapshot(diagram).to_dict() == before
