import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestBlock:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")

        for command in (
            DiagramCommand("configure", {"padding": 12, "wrap": False}),
            DiagramCommand("set_columns", {"columns": 3}),
            DiagramCommand("add_block", {"id": "front", "label": 'Front "end"', "span": 2}),
            DiagramCommand("add_space", {"id": "gap", "span": 1}),
            DiagramCommand("add_group", {"id": "back", "label": "Back end", "columns": 2, "span": 3}),
            DiagramCommand("add_block", {"id": "api", "label": "API", "parent_id": "back"}),
        ):
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("block").commands) == {
            "configure",
            "set_columns",
            "add_block",
            "add_space",
            "add_group",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'front["Front \\"end\\""]' in source
        assert "space" in source
        assert "block:back" in source
        assert application.render(restored) == source

    def test_rejects_invalid_columns_duplicates_and_unknown_parents(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.apply(diagram, DiagramCommand("add_block", {"id": "item", "label": "Item"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("set_columns", {"columns": "three"}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_block", {"id": "item", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_block", {"id": "nested", "label": "Nested", "parent_id": "missing"})
            )
