import json

import pytest
from contracts.mutation_conformance import assert_mutation_conformance

from mermaiden.application import Application, DiagramCommand, UnknownCommand


class TestRequirementDiagram:
    def test_exercises_every_public_command_including_removal_and_restores_mermaid(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("requirementDiagram")

        commands = (
            DiagramCommand("configure", {"rectMinWidth": 240, "fontSize": 16}),
            DiagramCommand(
                "add_requirement",
                {
                    "id": "login",
                    "requirement_id": "REQ-1",
                    "text": 'Users "sign in"',
                    "requirement_type": "functionalRequirement",
                    "risk": "high",
                    "verification_method": "test",
                },
            ),
            DiagramCommand(
                "add_element", {"id": "suite", "element_type": "test", "document_reference": "tests/login.py"}
            ),
            DiagramCommand(
                "add_relation",
                {"id": "verifies", "source_id": "suite", "target_id": "login", "relation_kind": "verifies"},
            ),
            DiagramCommand("remove_relation", {"id": "verifies"}),
            DiagramCommand(
                "add_relation",
                {"id": "verifies_again", "source_id": "suite", "target_id": "login", "relation_kind": "verifies"},
            ),
        )
        for command in commands:
            application.apply(diagram, command)

        assert_mutation_conformance(application, application.snapshot(diagram).to_dict())
        source = application.render(diagram)
        restored = application.restore(json.loads(json.dumps(application.snapshot(diagram).to_dict())))

        assert set(application.diagram_description("requirementDiagram").commands) == {
            item.operation for item in commands
        } | {
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
        assert "r_v_suite - verifies -> r_v_login" in source
        assert "verifies_again" not in source
        assert application.render(restored) == source

    def test_rejects_invalid_enums_duplicates_unknown_references_and_missing_removals(self) -> None:
        application = Application.create()
        diagram = application.create_diagram("requirementDiagram")
        command = DiagramCommand("add_requirement", {"id": "req", "requirement_id": "REQ-1", "text": "Text"})
        application.apply(diagram, command)

        with pytest.raises(UnknownCommand):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_requirement", {"id": "bad", "requirement_id": "REQ-2", "text": "Bad", "risk": "catastrophic"}
                ),
            )
        with pytest.raises(RuntimeError, match=r"already exists"):
            application.apply(diagram, command)
        with pytest.raises(RuntimeError, match=r"unknown|does not exist"):
            application.apply(
                diagram,
                DiagramCommand(
                    "add_relation",
                    {"id": "bad_relation", "source_id": "req", "target_id": "missing", "relation_kind": "contains"},
                ),
            )
        with pytest.raises(RuntimeError, match=r"does not exist|unknown"):
            application.apply(diagram, DiagramCommand("remove_relation", {"id": "missing"}))
