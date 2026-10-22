import json

import pytest

from mermaiden import Application


class TestBlock:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        for command in (
            ("configure", {"padding": 12, "wrap": False}),
            ("set_columns", {"columns": 3}),
            ("add_block", {"id": "front_example", "label": 'Front "end"', "span": 2}),
            ("add_space", {"id": "gap_example", "span": 1}),
            ("add_group", {"id": "back_example", "label": "Back end", "columns": 2, "span": 3}),
            ("add_block", {"id": "api_example", "label": "API", "parent_id": "back_example"}),
        ):
            application.execute(diagram, *command)
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
        assert 'front_example["Front \\"end\\""]' in source
        assert "space" in source
        assert "block:back_example" in source
        assert application.render(restored) == source

    def test_rejects_invalid_columns_duplicates_and_unknown_parents(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("block")
        application.execute(diagram, "add_block", {"id": "item_example", "label": "Item"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "set_columns", {"columns": "three"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_block", {"id": "item_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_block", {"id": "nested_example", "label": "Nested", "parent_id": "missing_example"}
            )
