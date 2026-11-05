import json
from xml.etree import ElementTree

import pytest

from mermaiden import Application


class TestSankey:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")
        commands = (
            ("configure", {"wrap": False}),
            ("add_node", {"id": "grid_example", "label": 'Grid, "main"'}),
            ("add_node", {"id": "homes_example", "label": "Homes"}),
            (
                "add_flow",
                {"id": "supply_example", "source_id": "grid_example", "target_id": "homes_example", "value": 113.726},
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("sankey").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert '"Grid#44; #34;main#34;","Homes",113.726' in source
        assert application.render(restored) == source

    def test_rejects_non_positive_flows_duplicates_and_unknown_nodes(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("sankey")
        application.execute(diagram, "add_node", {"id": "grid_example", "label": "Grid"})
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_flow",
                {"id": "bad_example", "source_id": "grid_example", "target_id": "grid_example", "value": "negative"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_node", {"id": "grid_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_flow",
                {"id": "missing_example", "source_id": "grid_example", "target_id": "missing_example", "value": 1},
            )

    def test_rejects_label_collisions_without_changing_the_graph(self) -> None:
        with Application.create() as application:
            diagram = application.create_diagram("sankey")
            application.execute(diagram, "add_node", {"id": "first_example", "label": "First example"})
            application.execute(diagram, "add_node", {"id": "second_example", "label": "Second example"})
            application.execute(
                diagram,
                "add_flow",
                {"id": "flow_example", "source_id": "first_example", "target_id": "second_example", "value": 4},
            )
            before = application.snapshot(diagram).to_dict()
            source = application.render(diagram)
            with pytest.raises(RuntimeError, match="labels must be unique"):
                application.execute(diagram, "add_node", {"id": "duplicate_example", "label": "First example"})
            with pytest.raises(RuntimeError, match="labels must be unique"):
                application.execute(
                    diagram,
                    "update_element",
                    {"id": "second_example", "kind": "sankey_node", "changes": {"label": "First example"}},
                )
            assert application.snapshot(diagram).to_dict() == before
            assert application.render(diagram) == source
            poisoned = json.loads(json.dumps(before))
            poisoned["elements"][1]["fields"]["label"] = "First example"
            with pytest.raises(RuntimeError, match="labels must be unique"):
                application.restore(poisoned)
            application.execute(
                diagram,
                "update_element",
                {"id": "second_example", "kind": "sankey_node", "changes": {"label": "Recovered example"}},
            )
            restored = application.restore(application.snapshot(diagram).to_dict())
            assert '"First example","Recovered example",4.0' in application.render(restored)

    @pytest.mark.integration
    def test_preserves_distinct_literal_labels_and_their_colors(self) -> None:
        labels = ("<b>Example</b>", "Example", "Literal &amp; &#34; #59;", 'Example — Łódź 🙂, "quoted"')
        with Application.create() as application:
            diagram = application.create_diagram("sankey")
            for index, label in enumerate(labels):
                application.execute(diagram, "add_node", {"id": f"node_{index}_example", "label": label})
            for index in range(3):
                application.execute(
                    diagram,
                    "add_flow",
                    {
                        "id": f"flow_{index}_example",
                        "source_id": f"node_{index}_example",
                        "target_id": f"node_{index + 1}_example",
                        "value": index + 1,
                    },
                )
            application.execute(diagram, "configure", {"show_values": False, "node_colors": {labels[0]: "#123456"}})
            before = application.snapshot(diagram).to_dict()
            restored = application.restore(before)
            report = application.validate_render(restored)
            assert report.success, report.diagnostics
            svg = ElementTree.fromstring(report.svg)
            assert tuple("".join(item.itertext()) for item in svg.iter("{http://www.w3.org/2000/svg}text")) == labels
            nodes = tuple(item for item in svg.iter() if item.attrib.get("class") == "node")
            assert len(nodes) == 4
            assert next(nodes[0].iter("{http://www.w3.org/2000/svg}rect")).attrib["fill"] == "#123456"
            assert application.snapshot(restored).to_dict() == before
