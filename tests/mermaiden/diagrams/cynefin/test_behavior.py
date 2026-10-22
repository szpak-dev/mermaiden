import json

import pytest

from mermaiden import Application


class TestCynefin:
    def test_exercises_configuration_and_rejects_invalid_public_arguments(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.execute(diagram, "configure", {"width": 960, "showDomainDescriptions": False})
        application.execute(diagram, "add_item", {"id": "example", "label": "Example", "domain": "clear"})
        assert '"width": 960.0' in application.render(diagram)
        assert set(application.diagram_description("cynefin-beta").commands) == {
            "configure",
            "add_item",
            "add_transition",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_item", {"id": "bad_example", "label": "Bad", "domain": "unknown"})

    def test_rejects_duplicate_items_and_unknown_transition_targets(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.execute(diagram, "add_item", {"id": "complex_example", "label": "Investigate", "domain": "complex"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_item", {"id": "complex_example", "label": "Again", "domain": "complex"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_transition",
                {"id": "missing_example", "source_id": "complex_example", "target_id": "missing_example"},
            )

    def test_renders_every_domain_in_canonical_order(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        for id, label, domain in (
            ("clear_example", "Clear item", "clear"),
            ("confusion_example", "Confusion item", "confusion"),
            ("complex_example", "Complex item", "complex"),
            ("chaotic_example", "Chaotic item", "chaotic"),
            ("complicated_example", "Complicated item", "complicated"),
        ):
            application.execute(diagram, "add_item", {"id": id, "label": label, "domain": domain})
        body = application.render(diagram).split("---\n", maxsplit=2)[2]
        expected = (
            'cynefin-beta\ncomplex\n  "Complex item"\ncomplicated\n  "Complicated item"\n'
            'clear\n  "Clear item"\nchaotic\n  "Chaotic item"\nconfusion\n  "Confusion item"\n'
        )
        assert body == expected

    def test_omits_empty_domains(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.execute(
            diagram, "add_item", {"id": "complex_example", "label": "Complex item", "domain": "complex"}
        )
        application.execute(diagram, "add_item", {"id": "clear_example", "label": "Clear item", "domain": "clear"})
        body = application.render(diagram).split("---\n", maxsplit=2)[2]
        assert body == 'cynefin-beta\ncomplex\n  "Complex item"\nclear\n  "Clear item"\n'

    def test_preserves_domains_and_transitions_through_snapshot_restoration(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("cynefin-beta")
        application.execute(diagram, "add_item", {"id": "complex_example", "label": "Investigate", "domain": "complex"})
        application.execute(
            diagram, "add_item", {"id": "complicated_example", "label": "Analyze", "domain": "complicated"}
        )
        application.execute(
            diagram,
            "add_transition",
            {
                "id": "pattern_example",
                "source_id": "complex_example",
                "target_id": "complicated_example",
                "label": "Pattern identified",
            },
        )
        source = application.render(diagram)
        snapshot = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
        restored = application.restore(snapshot)
        assert application.render(restored) == source
        assert 'complex --> complicated : "Pattern identified"' in source
