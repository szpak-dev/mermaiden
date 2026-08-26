import json

import pytest

from mermaiden.application import Application, DiagramCommand


class TestWardley:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("wardley-beta")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand(
                "add_anchor", {"id": "business", "label": 'Business "goal"', "visibility": 0.95, "evolution": 0.63}
            ),
            DiagramCommand(
                "add_component",
                {"id": "tea", "label": "Cup of Tea", "visibility": 0.79, "evolution": 0.61, "decorator": "build"},
            ),
            DiagramCommand(
                "add_dependency", {"id": "needs", "source_id": "business", "target_id": "tea", "label": "needs"}
            ),
            DiagramCommand("add_evolution", {"id": "evolve", "component_id": "tea", "target": 0.89}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("wardley-beta").commands) == {item.operation for item in commands}
        assert 'anchor "Business \\"goal\\"" [0.95, 0.63]' in source
        assert 'component "Cup of Tea" [0.79, 0.61] (build)' in source
        assert '"Business \\"goal\\"" -> "Cup of Tea"; needs' in source
        assert 'evolve "Cup of Tea" 0.89' in source
        assert application.render(restored) == source

    def test_rejects_out_of_range_positions_duplicates_and_unknown_components(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("wardley-beta")
        application.apply(
            diagram, DiagramCommand("add_component", {"id": "tea", "label": "Tea", "visibility": 0.5, "evolution": 0.5})
        )

        with pytest.raises(RuntimeError, match=r"coordinates must be between 0 and 1"):
            application.apply(
                diagram, DiagramCommand("add_anchor", {"id": "bad", "label": "Bad", "visibility": 2, "evolution": 0.5})
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(
                diagram,
                DiagramCommand("add_component", {"id": "tea", "label": "Again", "visibility": 0.5, "evolution": 0.5}),
            )
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_evolution", {"id": "missing", "component_id": "missing", "target": 0.8})
            )
