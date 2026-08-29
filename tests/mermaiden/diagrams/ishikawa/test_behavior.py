import json

import pytest

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestIshikawa:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("ishikawa-beta")

        commands = (
            DiagramCommand("configure", {"wrap": False}),
            DiagramCommand("add_effect", {"id": "effect", "label": 'Blurry "photo"'}),
            DiagramCommand("add_category", {"id": "equipment", "label": "Equipment"}),
            DiagramCommand("add_category", {"id": "lens", "label": "Lens", "parent_id": "equipment"}),
            DiagramCommand("add_cause", {"id": "damage", "label": "Damaged lens", "parent_id": "lens"}),
        )
        for command in commands:
            application.apply(diagram, command)

        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("ishikawa-beta").commands) == {
            item.operation for item in commands
        } | {"update_element", "remove_element", "update_relation", "remove_relation"}
        for fragment in (
            'Blurry "photo"',
            "Equipment",
            "  Lens",
            "    Damaged lens",
        ):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_categories(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("ishikawa-beta")
        application.apply(diagram, DiagramCommand("add_effect", {"id": "effect", "label": "Effect"}))
        application.apply(diagram, DiagramCommand("add_category", {"id": "category", "label": "Category"}))

        with pytest.raises(UnknownCommand):
            application.apply(diagram, DiagramCommand("configure", {"missing": True}))
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, DiagramCommand("add_category", {"id": "category", "label": "Again"}))
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram, DiagramCommand("add_cause", {"id": "cause", "label": "Cause", "parent_id": "missing"})
            )
