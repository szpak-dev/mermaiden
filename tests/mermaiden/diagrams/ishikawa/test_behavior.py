import json

import pytest

from mermaiden import Application


class TestIshikawa:
    def test_exercises_every_public_command_and_restores_identical_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("ishikawa-beta")
        commands = (
            ("configure", {"wrap": False}),
            ("add_effect", {"id": "effect_example", "label": 'Blurry "photo"'}),
            ("add_category", {"id": "equipment_example", "label": "Equipment"}),
            ("add_category", {"id": "lens_example", "label": "Lens", "parent_id": "equipment_example"}),
            ("add_cause", {"id": "damage_example", "label": "Damaged lens_example", "parent_id": "lens_example"}),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("ishikawa-beta").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        for fragment in ('Blurry "photo"', "Equipment", "  Lens", "    Damaged lens_example"):
            assert fragment in source
        assert application.render(restored) == source

    def test_rejects_invalid_configuration_duplicates_and_unknown_categories(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("ishikawa-beta")
        application.execute(diagram, "add_effect", {"id": "effect_example", "label": "Effect"})
        application.execute(diagram, "add_category", {"id": "category_example", "label": "Category"})
        with pytest.raises(RuntimeError):
            application.execute(diagram, "configure", {"missing_example": True})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_category", {"id": "category_example", "label": "Again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram, "add_cause", {"id": "cause_example", "label": "Cause", "parent_id": "missing_example"}
            )
