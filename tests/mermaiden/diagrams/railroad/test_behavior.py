import json

import pytest

from mermaiden import Application


class TestRailroadIncrementalCommands:
    def test_exercises_configuration_and_rejects_invalid_public_arguments(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("railroad-ebnf-beta")
        application.execute(diagram, "configure", {"compactMode": True, "fontSize": 16})
        application.execute(diagram, "add_rule", {"id": "example", "label": "example"})
        assert '"compactMode": true' in application.render(diagram)
        assert set(application.diagram_description("railroad-ebnf-beta").commands) == {
            "configure",
            "add_alternative",
            "add_group",
            "add_non_terminal",
            "add_optional",
            "add_repetition",
            "add_rule",
            "add_special",
            "add_terminal",
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
        }
        with pytest.raises(RuntimeError):
            application.execute(diagram, "add_rule", {"id": "bad_example"})

    def test_rejects_duplicate_rules_and_unknown_expression_parents(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("railroad-ebnf-beta")
        application.execute(diagram, "add_rule", {"id": "rule_example", "label": "rule_example"})
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, "add_rule", {"id": "rule_example", "label": "again"})
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_special",
                {"id": "value_example", "label": "value_example", "parent_id": "missing_example"},
            )

    def test_persists_a_valid_revision_after_every_container_command(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("railroad-ebnf-beta")
        revisions = (
            (("add_rule", {"id": "example_rule", "label": "example"}), 'r_v_example_rule = "" ;'),
            (
                ("add_alternative", {"id": "example_alternative", "parent_id": "example_rule"}),
                'r_v_example_rule = "" ;',
            ),
            (
                ("add_special", {"id": "example_value", "label": "value_example", "parent_id": "example_alternative"}),
                "r_v_example_rule = ? value_example ? ;",
            ),
            (
                ("add_optional", {"id": "example_optional", "parent_id": "example_alternative"}),
                'r_v_example_rule = ? value_example ? | [ "" ] ;',
            ),
            (
                ("add_terminal", {"id": "optional_value_example", "label": "optional", "rule_id": "example_optional"}),
                'r_v_example_rule = ? value_example ? | [ "optional" ] ;',
            ),
            (
                ("add_repetition", {"id": "example_repetition", "parent_id": "example_alternative"}),
                'r_v_example_rule = ? value_example ? | [ "optional" ] | { "" } ;',
            ),
            (
                (
                    "add_non_terminal",
                    {"id": "repeated_value_example", "label": "repeated", "rule_id": "example_repetition"},
                ),
                'r_v_example_rule = ? value_example ? | [ "optional" ] | { repeated } ;',
            ),
            (
                ("add_group", {"id": "example_group", "parent_id": "example_alternative"}),
                'r_v_example_rule = ? value_example ? | [ "optional" ] | { repeated } | ( "" ) ;',
            ),
            (
                ("add_special", {"id": "grouped_value_example", "label": "grouped", "parent_id": "example_group"}),
                'r_v_example_rule = ? value_example ? | [ "optional" ] | { repeated } | ( ? grouped ? ) ;',
            ),
        )
        for command, expected_source in revisions:
            report = application.execute(diagram, *command)
            persisted = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
            diagram = application.restore(persisted)
            assert report is not None
            assert report.accepted
            assert expected_source in application.render(diagram)
