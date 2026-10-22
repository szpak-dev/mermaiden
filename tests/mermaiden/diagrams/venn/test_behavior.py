import json

import pytest

from mermaiden import Application


class TestVenn:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("venn-beta")
        commands = (
            ("configure", {"width": 640, "height": 360, "useDebugLayout": True}),
            ("add_set", {"id": "front_example", "label": 'Front "end"', "size": 20}),
            ("add_set", {"id": "back_example", "label": "Back end", "size": 12}),
            ("add_text", {"id": "react_example", "label": "React", "parent_id": "front_example"}),
            (
                "add_union",
                {"id": "shared_example", "label": "Shared", "set_ids": ["front_example", "back_example"], "size": 3},
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("venn-beta").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'set front_example["Front \\"end\\""]:20' in source
        assert 'text react_example["React"]' in source
        assert 'union front_example,back_example["Shared"]:3' in source
        assert application.render(restored) == source

    def test_rejects_invalid_sizes_bad_union_arguments_and_unknown_sets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("venn-beta")
        application.execute(diagram, "add_set", {"id": "one_example", "label": "One", "size": 1})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_set", {"id": "bad_example", "label": "Bad", "size": "large"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_union", {"id": "few_example", "label": "Few", "set_ids": "one_example"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_text", {"id": "text_example", "label": "Text", "parent_id": "missing_example"}
            )
