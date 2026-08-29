import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestVenn:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("venn-beta")

        commands = (
            DiagramCommand("configure", {"width": 640, "height": 360, "useDebugLayout": True}),
            DiagramCommand("add_set", {"id": "front", "label": 'Front "end"', "size": 20}),
            DiagramCommand("add_set", {"id": "back", "label": "Back end", "size": 12}),
            DiagramCommand("add_text", {"id": "react", "label": "React", "parent_id": "front"}),
            DiagramCommand("add_union", {"id": "shared", "label": "Shared", "set_ids": ["front", "back"], "size": 3}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("venn-beta").commands) == {item.operation for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        assert 'set front["Front \\"end\\""]:20' in source
        assert 'text react["React"]' in source
        assert 'union front,back["Shared"]:3' in source
        assert application.render(restored) == source

    def test_rejects_invalid_sizes_bad_union_arguments_and_unknown_sets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("venn-beta")
        application.apply(diagram, DiagramCommand("add_set", {"id": "one", "label": "One", "size": 1}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("add_set", {"id": "bad", "label": "Bad", "size": "large"}))
        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("add_union", {"id": "few", "label": "Few", "set_ids": "one"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_text", {"id": "text", "label": "Text", "parent_id": "missing"})
            )
