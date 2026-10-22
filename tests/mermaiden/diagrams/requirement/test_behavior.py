import json

import pytest

from mermaiden import Application


class TestRequirementDiagram:
    def test_exercises_every_public_command_including_removal_and_restores_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("requirementDiagram")
        commands = (
            ("configure", {"rect_min_width": 240, "fontSize": 16}),
            (
                "add_requirement",
                {
                    "id": "login_example",
                    "requirement_id": "REQ-1",
                    "text": 'Users "sign in"',
                    "requirement_type": "functionalRequirement",
                    "risk": "high",
                    "verification_method": "test",
                },
            ),
            (
                "add_element",
                {"id": "suite_example", "element_type": "test", "document_reference": "tests/login_example.py"},
            ),
            (
                "add_relation",
                {
                    "id": "verifies_example",
                    "source_id": "suite_example",
                    "target_id": "login_example",
                    "relation_kind": "verifies",
                },
            ),
            ("remove_relation", {"id": "verifies_example"}),
            (
                "add_relation",
                {
                    "id": "verifies_again_example",
                    "source_id": "suite_example",
                    "target_id": "login_example",
                    "relation_kind": "verifies",
                },
            ),
        )
        for command in commands:
            application.execute(diagram, *command)
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))
        assert set(application.diagram_description("requirementDiagram").commands) == {item[0] for item in commands} | {
            "update_element",
            "remove_element",
            "move_element",
            "reorder_elements",
            "update_relation",
            "remove_relation",
        }
        assert "functionalRequirement" in source
        assert 'text: "Users \\"sign in\\""' in source
        assert "element" in source
        assert "r_v_suite_example - verifies -> r_v_login_example" in source
        assert "verifies_again_example" not in source
        assert application.render(restored) == source

    def test_rejects_invalid_enums_duplicates_unknown_references_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("requirementDiagram")
        command = ("add_requirement", {"id": "req_example", "requirement_id": "REQ-1", "text": "Text"})
        application.execute(diagram, *command)
        with pytest.raises(RuntimeError):
            application.execute(
                diagram,
                "add_requirement",
                {"id": "bad_example", "requirement_id": "REQ-2", "text": "Bad", "risk": "catastrophic"},
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.execute(diagram, *command)
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.execute(
                diagram,
                "add_relation",
                {
                    "id": "bad_relation_example",
                    "source_id": "req_example",
                    "target_id": "missing_example",
                    "relation_kind": "contains",
                },
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.execute(diagram, "remove_relation", {"id": "missing_example"})
