import json

from mermaiden.application import Application, DiagramCommand


class TestRailroadIncrementalCommands:
    def test_persists_a_valid_revision_after_every_container_command(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("railroad-ebnf-beta")
        revisions = (
            (
                DiagramCommand("add_rule", {"id": "example_rule", "label": "example"}),
                'r_v_example_rule = "" ;',
            ),
            (
                DiagramCommand("add_alternative", {"id": "example_alternative", "parent_id": "example_rule"}),
                'r_v_example_rule = "" ;',
            ),
            (
                DiagramCommand(
                    "add_special",
                    {"id": "example_value", "label": "value", "parent_id": "example_alternative"},
                ),
                "r_v_example_rule = ? value ? ;",
            ),
            (
                DiagramCommand("add_optional", {"id": "example_optional", "parent_id": "example_alternative"}),
                'r_v_example_rule = ? value ? | [ "" ] ;',
            ),
            (
                DiagramCommand(
                    "add_terminal",
                    {"id": "optional_value", "label": "optional", "rule_id": "example_optional"},
                ),
                'r_v_example_rule = ? value ? | [ "optional" ] ;',
            ),
            (
                DiagramCommand(
                    "add_repetition",
                    {"id": "example_repetition", "parent_id": "example_alternative"},
                ),
                'r_v_example_rule = ? value ? | [ "optional" ] | { "" } ;',
            ),
            (
                DiagramCommand(
                    "add_non_terminal",
                    {"id": "repeated_value", "label": "repeated", "rule_id": "example_repetition"},
                ),
                'r_v_example_rule = ? value ? | [ "optional" ] | { repeated } ;',
            ),
            (
                DiagramCommand("add_group", {"id": "example_group", "parent_id": "example_alternative"}),
                'r_v_example_rule = ? value ? | [ "optional" ] | { repeated } | ( "" ) ;',
            ),
            (
                DiagramCommand(
                    "add_special",
                    {"id": "grouped_value", "label": "grouped", "parent_id": "example_group"},
                ),
                "r_v_example_rule = ? value ? | [ \"optional\" ] | { repeated } | ( ? grouped ? ) ;",
            ),
        )

        for command, expected_source in revisions:
            report = application.apply(diagram, command)
            persisted = json.loads(json.dumps(application.snapshot(diagram).to_dict()))
            diagram = application.restore(persisted)

            assert report is not None
            assert report.accepted
            assert expected_source in application.render(diagram)
