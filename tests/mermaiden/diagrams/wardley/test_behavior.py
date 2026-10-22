import json

import pytest

from mermaiden import Application


class TestWardley:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("wardley-beta")
        commands = (
            ("configure", {"wrap": False}),
            (
                "add_anchor",
                {"id": "business_example", "label": 'Business "goal"', "visibility": 0.95, "evolution": 0.63},
            ),
            (
                "add_component",
                {
                    "id": "tea_example",
                    "label": "Cup of Tea",
                    "visibility": 0.79,
                    "evolution": 0.61,
                    "decorators": ["build"],
                },
            ),
            (
                "add_dependency",
                {
                    "id": "needs_example",
                    "source_id": "business_example",
                    "target_id": "tea_example",
                    "label": "needs_example",
                },
            ),
            ("add_evolution", {"id": "evolve_example", "component_id": "tea_example", "target": 0.89}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("wardley-beta").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert 'anchor "Business \\"goal\\"" [0.95, 0.63]' in source
        assert 'component "Cup of Tea" [0.79, 0.61] (build)' in source
        assert '"Business \\"goal\\"" -> "Cup of Tea"; needs_example' in source
        assert 'evolve "Cup of Tea" 0.89' in source
        assert application.render(restored) == source

    def test_rejects_out_of_range_positions_duplicates_and_unknown_components(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("wardley-beta")
        application.execute(
            diagram, "add_component", {"id": "tea_example", "label": "Tea", "visibility": 0.5, "evolution": 0.5}
        )
        with pytest.raises(RuntimeError, match=r"coordinates must be between 0 and 1"):
            application.execute(
                diagram, "add_anchor", {"id": "bad_example", "label": "Bad", "visibility": 2, "evolution": 0.5}
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(
                diagram, "add_component", {"id": "tea_example", "label": "Again", "visibility": 0.5, "evolution": 0.5}
            )
        for decorators in (["custom"], ["build", "buy"]):
            with pytest.raises(RuntimeError):
                application.execute(
                    diagram,
                    "add_component",
                    {
                        "id": "invalid_example",
                        "label": "Invalid",
                        "visibility": 0.5,
                        "evolution": 0.5,
                        "decorators": decorators,
                    },
                )
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_evolution", {"id": "missing_example", "component_id": "missing_example", "target": 0.8}
            )
